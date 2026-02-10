from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Simulation
from evaluation.models import TaskSubmission
from .agents import * # We will build this next
from django.shortcuts import get_object_or_404, redirect
from agents.models import Conversation, Message
from .models import Simulation
from django.http import JsonResponse
# simulation/views.py
from .agents import TaskEvaluatorAgent      
# simulation/views.py
import asyncio
from playwright.async_api import async_playwright
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Simulation

@login_required
def delete_simulation(request, sim_id):
    if request.method == "POST":
        simulation = get_object_or_404(Simulation, id=sim_id, user=request.user)
        simulation.delete()
    return redirect('dashboard')

@login_required
def resume_simulation(request, sim_id):
    # Logic to find where the user left off and redirect to chat
    return redirect('simulation_chat', simulation_id=sim_id)

@login_required
def create_simulation(request):
    if request.method == "POST":
        role = request.POST.get('job_role')
        edu = request.POST.get('education')
        
        # Fast Database entry
        sim = Simulation.objects.create(
            user=request.user, 
            role_title=role,
            status='ongoing'
        )
        # Store education in profile if needed
        return render(request, 'loading.html', {'simulation_id': sim.id})



@login_required
def initiate_ai_logic(request, simulation_id):
    try:
        sim = Simulation.objects.get(id=simulation_id, user=request.user)
        
        # Step 1: Thinker designs Project (Title/Desc/Agents)
        thinker = ThinkerAgent()
        project_info = thinker.generate_project(sim.role_title, "User technical background")
        if not project_info: raise Exception("Thinker Error")
        
        sim.project_title = project_info.get('title')
        sim.description = project_info.get('description')
        names = project_info.get('agents', {})
        print("Names:",names)
        sim.hr_name = names.get('hr_name', 'Sarah')
        sim.peer_name = names.get('peer_name', 'Alex')
        sim.client_name = names.get('client_name', 'Michael')
        sim.save()

        # Step 2: Planner breaks it into 5-7 Tasks
        planner = PlannerAgent()
        if not planner.create_subtasks(sim): raise Exception("Planner Error")
        
        # Step 3: Setup Conversations & HR Greeting
        for role in ['HR', 'PEER', 'CLIENT']:
            Conversation.objects.get_or_create(
                simulation=sim, agent_type=role,
                defaults={'session_id': f"sim_{sim.id}_{role.lower()}"}
            )

        hr_conv = Conversation.objects.get(simulation=sim, agent_type='HR')
        intro_text = f"Hello! I'm your HR lead. We are starting project '{sim.project_title}'."
        Message.objects.create(conversation=hr_conv, sender="HR", text=intro_text)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def simulation_chat(request, simulation_id):
    sim = get_object_or_404(Simulation, id=simulation_id, user=request.user)
    
    # Get all subtasks for the sidebar
    tasks = sim.tasks.all().order_by('order')
    current_task = tasks.filter(is_completed=False).first()
    completed_tasks =  tasks.filter(is_completed=True).order_by('-order')
    # Get conversations for the three tabs
    conv_dict = {
            'hr': Conversation.objects.filter(simulation=sim, agent_type='HR').first(),
            'peer': Conversation.objects.filter(simulation=sim, agent_type='PEER').first(),
            'client': Conversation.objects.filter(simulation=sim, agent_type='CLIENT').first(),
        }
    tasks = sim.tasks.all().order_by('order')
    current_task = tasks.filter(is_completed=False).first()
    messages = Message.objects.filter(conversation__simulation=sim).order_by('timestamp')
    context = {
        'sim': sim,
        'conversations': conv_dict,  # This must be the dictionary
        'messages': messages,
        'current_task': current_task,
        'completed_tasks': completed_tasks,
        'agent_list': ['hr', 'peer', 'client'], # Useful for the loop
    }
    print(completed_tasks)
    return render(request, 'simulation_chat.html', context)


@login_required
def send_message(request):
    if request.method == "POST":
        conv_id = request.POST.get('conversation_id')
        user_text = request.POST.get('text')
        
        conv = get_object_or_404(Conversation, id=conv_id, simulation__user=request.user)
        sim = conv.simulation
        
        # 1. Save User Message
        Message.objects.create(conversation=conv, sender="User", text=user_text)

        # 2. Trigger AI Response based on Agent Type
        agent = ConversationAgent(role_type=conv.agent_type)
        ai_response = agent.get_response(sim, user_text)
        
        # 3. Save Agent Message
        Message.objects.create(conversation=conv, sender=conv.agent_type, text=ai_response)

        # 4. Trigger Summarizer every 10 messages (Shared Memory)
        if conv.messages.count() % 10 == 0:
            summarizer = SummarizerAgent()
            summarizer.summarize_chat(conv)

        return redirect('simulation_chat', simulation_id=sim.id)


@login_required
def submit_task(request):
    if request.method == "POST":
        sim_id = request.POST.get('simulation_id')
        task_id = request.POST.get('task_id')
        zip_file = request.FILES.get('project_zip')
        
        simulation = get_object_or_404(Simulation, id=sim_id, user=request.user)
        task = get_object_or_404(Task, id=task_id, simulation=simulation)
        
        # Increment attempt counter
        task.attempts += 1
        task.save()

        # 1. GENERATE/RETRIEVE EXPECTED OUTPUT
        # Only generate if it doesn't exist to save API costs
        if not simulation.expected_output_template:
            thinker = ThinkerAgent()
            simulation.expected_output_template = thinker.generate_task_solution(
                simulation.project_title, task.instruction
            )
            simulation.save()
        
        # 2. EVALUATE
        evaluator = TaskEvaluatorAgent()
        result_text = evaluator.evaluate(simulation, task, zip_file)
        
        # 3. PARSE RESULTS
        try:
            score = int(''.join(filter(str.isdigit, result_text.split('|')[0])))
            feedback = result_text.split('|')[1].replace('FEEDBACK:', '').strip()
        except:
            score, feedback = 0, "Evaluation parsing failed."

        # 4. DECISION LOGIC (The 3-Tries Rule)
        is_last_attempt = (task.attempts >= 3)
        passed = (score >= 70) # Threshold for success

        peer_conv = Conversation.objects.filter(simulation=simulation, agent_type='PEER').first()
        
        if passed:
            task.is_completed = True
            msg_text = f"Great work! Your submission for {task.title} passed with {score}%. {feedback}"
        elif not passed and not is_last_attempt:
            # User failed but has tries left
            msg_text = f"I've reviewed your submission for {task.title}. Score: {score}%. It's not quite there yet. Feedback: {feedback}. You have {3-task.attempts} attempts left."
        else:
            # Final failure: Give solution and move on
            task.is_completed = True
            msg_text = f"I've reviewed your third attempt for {task.title}. Score: {score}%. Feedback: {feedback}. Look, let's not get stuck here. Here is the expected logic/code: \n\n{simulation.expected_output_template}... \n\nLet's move to the next task."
            # Clear template for next task
            simulation.expected_output_template = "" 
            simulation.save()
        TaskSubmission.objects.create(
            task=task,
            zip_file=zip_file,
            attempt_number=task.attempts,
            score=score,
            feedback=feedback,
            is_success=(score >= 70)
        )
        task.score = score
        task.feedback = feedback
        task.save()

        if peer_conv:
            Message.objects.create(conversation=peer_conv, sender="PEER", text=msg_text)
        
        return redirect('simulation_chat', simulation_id=sim_id)

@login_required
def send_message_ajax(request):
    conv_id = request.POST.get('conversation_id')
    text = request.POST.get('text')
    conv = get_object_or_404(Conversation, id=conv_id, simulation__user=request.user)
    sim = conv.simulation

    # 1. Save User Message for Performance Agent analysis
    Message.objects.create(conversation=conv, sender="User", text=text)

    # 2. Get AI Response based on Agent Type personality
    agent = ConversationAgent(role_type=conv.agent_type)
    ai_response = agent.get_response(sim, text)

    # 3. Save initial AI Message to database
    Message.objects.create(conversation=conv, sender=conv.agent_type, text=ai_response)
    if conv.agent_type == 'PEER':
        current_task = sim.tasks.filter(is_completed=False).order_by('order').first()
    # 4. Handle Progression for Discussion-only Tasks
    current_task = sim.tasks.filter(is_completed=False).order_by('order').first()
    task_updated = False
    all_tasks_done = False

    if current_task and not current_task.requires_submission:
        # Check if user indicates completion via keywords
        keywords = ['understand', 'understood', 'done', 'proceed', 'clear', 'ready', 'okay']
        if any(word in text.lower() for word in keywords):
            current_task.is_completed = True
            current_task.score = 100
            current_task.attempts = 1
            current_task.save()
            
            # Identify the new current task
            current_task = sim.tasks.filter(is_completed=False).order_by('order').first()
            task_updated = True
            
            if current_task:
                # Override ai_response for a smooth transition
                ai_response = f"Excellent. Since you're clear on that, let's move to: {current_task.title}. Check the Project Overview for instructions."
                
            else:
                # NO TASKS LEFT: Trigger HR Conclusion
                all_tasks_done = True
                sim.status = 'completed'
                sim.save()
                
                ai_response = f"Congratulations! You have successfully completed all milestones for the '{sim.project_title}' project. Thank you for your hard work. Your final performance report is now ready for review."
            # Sync the transition text back to the database
            last_msg = Message.objects.filter(conversation=conv).last()
            if last_msg:
                last_msg.text = ai_response
                last_msg.save()

    # 5. Return JSON with AI message and new task data for frontend sync
    return JsonResponse({
        'ai_message': ai_response,
        'task_updated': task_updated,
        'all_tasks_done': all_tasks_done,
        'new_task': {
            'title': current_task.title if current_task else "Project Completed",
            'instruction': current_task.instruction if current_task else "You have successfully completed all project milestones.",
            'requires_submission': current_task.requires_submission if current_task else False,
            'id': current_task.id if current_task else None
        } if current_task else None
    })

@login_required
def end_simulation_report(request, simulation_id):
    sim = get_object_or_404(Simulation, id=simulation_id, user=request.user)
    if not sim.final_report_data or request.GET.get('refresh') == 'true':
        sim.status = 'completed'
        # Trigger Performance Agent
        perf_agent = PerformanceAgent()
        report_data = perf_agent.generate_final_report(sim)
        sim.final_report_data = report_data
        # Save the status
        
        sim.save()

    return render(request, 'final_report.html', {
        'sim': sim,
        'report': sim.final_report_data
    })


# simulation/views.py
@login_required
def profile_view(request):
    # Fetch completed simulations to display as certificates
    completed_sims = Simulation.objects.filter(user=request.user, status='completed').order_by('-created_at')
    # Fetch all simulations for history
    activity_history = Simulation.objects.filter(user=request.user, status='ongoing').order_by('-created_at')

    return render(request, 'profile.html', {
        'user': request.user,
        'certificates': completed_sims,
        'history': activity_history
    })


def certificate_view(request, simulation_id):
    sim = get_object_or_404(Simulation, id=simulation_id)
    # Optional: security check
    # if not sim.is_completed:
    #     return HttpResponseForbidden("Certificate not available")
    report_data = sim.final_report_data
    return render(request, "certificate.html", {
        "user": sim.user,
        "sim": sim,
        'report': report_data
    })


# simulation/views.py


@login_required
def download_certificate_pdf(request, sim_id):
    # Ensure the user owns the completed simulation
    sim = get_object_or_404(Simulation, id=sim_id, user=request.user, status='completed')

    async def generate_pdf():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Pass the session cookie so the browser is "logged in"
            context = await browser.new_context()
            await context.add_cookies([{
                'name': 'sessionid',
                'value': request.COOKIES.get('sessionid'),
                'domain': '127.0.0.1',
                'path': '/'
            }])
            
            page = await context.new_page()
            # Navigate to the existing certificate page
            url = request.build_absolute_uri(f"/certificate/{sim_id}/")
            await page.goto(url)
            
            # Use a CSS selector to capture only the certificate
            # This hides the "Back to Profile" and "Download" buttons during print
            await page.add_style_tag(content="""
                @media print {
                    nav, .text-right, .text-center button { display: none !important; }
                    body { background: none !important; }
                    .certificate-bg { margin: 0 !important; border: none !important; }
                }
            """)

            pdf_bytes = await page.pdf(
                format="Letter",
                landscape=True,
                print_background=True # Ensures the blue gradient shows
            )
            await browser.close()
            return pdf_bytes

    # Run the async function in a synchronous Django view
    pdf_content = asyncio.run(generate_pdf())
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate_{sim.role_title}.pdf"'
    return response

























