import json
import requests
from django.conf import settings
from .models import *
from agents.models import *
import re
import zipfile
import io
import ast
# simulation/agents.py
import zipfile
import json
import requests
from django.conf import settings
import time
# simulation/agents.py

THINKING_MODELS = [
    "deepseek/deepseek-r1-0528:free",
    "tngtech/deepseek-r1t-chimera:free",
    "tngtech/deepseek-r1t2-chimera:free",
    "tngtech/tng-r1t-chimera:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
]

CODING_MODELS = [
    "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
]

FAST_CHAT_MODELS = [
    "arcee-ai/trinity-mini:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "google/gemma-3-4b-it:free",
    "google/gemma-3n-e4b-it:free",
]

HEAVY_REASONING_MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
]

EVALUATION_MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
]

GENERAL_PURPOSE_MODELS = [
    "z-ai/glm-4.5-air:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen3-4b:free",
]

# ============================================================
# BASE AGENT (SINGLE SOURCE OF TRUTH)
# ============================================================

class BaseAgent:
    def __init__(self, models):
        self.keys = settings.OPENROUTER_API_KEYS
        self.models = models

    def _call_openrouter(self, messages, json_mode=False, timeout=30):
        for model in self.models:
            for key in self.keys:
                try:
                    payload = {
                        "model": model,
                        "messages": messages
                    }
                    if json_mode:
                        payload["response_format"] = {"type": "json_object"}

                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key}",
                            "HTTP-Referer": "http://localhost:8000",
                            "Content-Type": "application/json"
                        },
                        data=json.dumps(payload),
                        timeout=timeout
                    )
                    print(response.json()["choices"][0]["message"]["content"])
                    if response.status_code == 200:
                        return self._clean(response.json()["choices"][0]["message"]["content"])
                except Exception:
                    continue
        return None

    def _clean(self, text):
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text.strip()

# ============================================================
# MANAGER AGENT
# ============================================================

# simulation/agents.py

class ManagerAgent(BaseAgent):
    def __init__(self):
        # Using reasoning models to handle the logic of task rewriting
        super().__init__(HEAVY_REASONING_MODELS + GENERAL_PURPOSE_MODELS)

    def adjust_difficulty(self, simulation, last_score):
        # Find the next task that isn't completed
        task = simulation.tasks.filter(is_completed=False).order_by("order").first()
        if not task:
            return

        # Determine the modification intent
        if last_score > 85:
            adjustment_type = "ADVANCED: Increase technical complexity, add edge cases, and use industry-standard constraints."
            new_difficulty = 3
        elif last_score < 55:
            adjustment_type = "SIMPLIFIED: Break the task down, provide more scaffolding, and focus on core fundamentals."
            new_difficulty = 1
        else:
            return # No change needed for average scores

        prompt = f"""
        You are the Technical Project Manager for '{simulation.project_title}'.
        The user just scored {last_score}% on their last task. 
        
        CURRENT TASK TO MODIFY:
        Title: {task.title}
        Original Instruction: {task.instruction}

        GOAL: Rewrite this task to be {adjustment_type}.
        Keep the core objective the same, but change the implementation requirements.
        
        Return JSON format:
        {{
            "title": "New Task Title",
            "instruction": "New detailed instruction set"
        }}
        """

        response = self._call_openrouter([{"role": "system", "content": prompt}], json_mode=True)
        
        if response:
            try:
                data = json.loads(response)
                task.title = data.get('title', task.title)
                task.instruction = data.get('instruction', task.instruction)
                task.difficulty = new_difficulty
                task.save()
            except Exception as e:
                print(f"ManagerAgent adjustment failed: {e}")
# ============================================================
# THINKER AGENT (PROJECT + SOLUTIONS)
# ============================================================

class ThinkerAgent(BaseAgent):
    def __init__(self):
        super().__init__(HEAVY_REASONING_MODELS + THINKING_MODELS)

    def generate_project(self, role, education):
        prompt = f"""
        Design a realistic, industry-relevant project for the given {role} role. User Education: {education}.
        Return JSON with: 'title', 'description', 'agents'.
        'agents' will inclue : 'hr_name', 'peer_name', 'client_name' in JSON format.
        """
        response = self._call_openrouter([{"role": "system", "content": prompt}], json_mode=True)
        return json.loads(response) if response else None

    def generate_task_solution(self, project_title, task_instruction):
        prompt = f"""
        You are an Expert Lead. For the project '{project_title}', provide the 'Perfect Answer' code 
        for this specific task: '{task_instruction}'. 
        Return ONLY the code solution.
        """
        return self._call_openrouter([{"role": "system", "content": prompt}])

# ============================================================
# PLANNER AGENT
# ============================================================

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(GENERAL_PURPOSE_MODELS + HEAVY_REASONING_MODELS)

    def create_subtasks(self, simulation):
        prompt = f"""
        Break the project '{simulation.project_title}' into 5-7 logical tasks.
        For each task, define if 'requires_submission' is true (code/design) or false (discussion).
        'expected_file_extension': If requires_submission is true, specify the extension (e.g., '.py', '.ipynb', '.csv', '.txt'). If false, use null.
        Assign each task to one of these agents: 'HR' (for onboarding/intro), 'Peer' (for technical help), or 'Client' (for requirements/feedback).
        Return JSON with a list of 'subtasks': ['order', 'title', 'instruction', 'assigned_agent', 'requires_submission', 'expected_file_extension'].
        """
        response = self._call_openrouter([{"role": "system", "content": prompt}], json_mode=True)
        if response:
            data = json.loads(response)
            for t in data.get('subtasks', []):
                Task.objects.create(
                    simulation=simulation,
                    title=t['title'],
                    instruction=t['instruction'],
                    order=t['order'],
                    requires_submission=t['requires_submission'],
                    expected_file_extension=t.get('expected_file_extension')
                )
            return True
        return False


# ============================================================
# CONVERSATION AGENT (HR / PEER / CLIENT)
# ============================================================

class ConversationAgent(BaseAgent):
    def __init__(self, role_type):
        super().__init__(FAST_CHAT_MODELS)
        self.role_type = role_type

    def get_response(self, simulation, user_message):
        # Get context: Project details and current task
        current_task = simulation.tasks.filter(is_completed=False).order_by('order').first()
        conversation = Conversation.objects.get(simulation=simulation, agent_type=self.role_type)
        history = conversation.messages.all().order_by('-timestamp')[:5]
        history_str = "\n".join([f"{m.sender}: {m.text}" for m in reversed(history)])
        if self.role_type == 'HR':
            agent_name = simulation.hr_name
        elif self.role_type == 'PEER':
            agent_name = simulation.peer_name
        else:
            agent_name = simulation.client_name
        # Define personalities as per project requirements
        prompts = {
            'HR': "You are the HR Representative. Be professional and guide the user on onboarding and administrative tasks.",
            'PEER': "You are a Team Peer. Be helpful and casual. Provide technical hints if the user is stuck.",
            'CLIENT': "You are the Client. Be business-oriented and ask for updates or add feature requests."
        }

        system_prompt = f"""
        You are {agent_name}, the {self.role_type} for the project '{simulation.project_title}'.
        
        CURRENT STATUS:
        Current Task: {current_task.title if current_task else "All tasks finished"}
        Instructions for user: {current_task.instruction if current_task else "None"}
        IDENTITY RULES:
        1. Always introduce yourself as {agent_name}. Never refer to yourself as 'Agent' or 'PEER'.
        2. Your personality should reflect a professional {self.role_type} in a {simulation.role_title} simulation.
        3. If you are the Peer, be supportive and technical. If HR, be professional and onboarding-focused. 
        4. Do not perform the tasks for the user, but provide guidance and hints.
        CONTEXT:
        The user is currently working on this project: {simulation.description}
        RULE: If you ({self.role_type}) are NOT the owner of the current task, 
        CONVERSATION HISTORY:
        {history_str}

        STRICT RULES:
        1. Look at the history. If you already greeted the user, DO NOT greet them again.
        2. If the user says they understand or are ready, acknowledge it and tell them to focus on the current task: {current_task.title}.
        3. Stay in character as {self.role_type}. Keep responses to 2 to 4 sentences.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self._call_openrouter(messages)

# ============================================================
# TASK EVALUATOR AGENT
# ============================================================


# simulation/agents.py

class SoftSkillsAgent(BaseAgent):
    def __init__(self):
        # Use fast models for real-time analysis during chat
        super().__init__(FAST_CHAT_MODELS)

    def analyze_message(self, text):
        prompt = f"""
        Analyze the professional soft skills in this user message: "{text}"
        
        Rate from 0-100:
        1. Professionalism: Use of appropriate workplace language and tone.
        2. Clarity: Directness and ease of understanding.
        3. Confidence: Level of certainty and lack of over-apologizing.

        Return ONLY a JSON object:
        {{
            "professionalism": 0-100,
            "clarity": 0-100,
            "confidence": 0-100
        }}
        """
        response = self._call_openrouter([{"role": "system", "content": prompt}], json_mode=True)
        try:
            return json.loads(response)
        except:
            return None

    def update_heatmap(self, simulation, new_scores):
        """Calculates a rolling average to update the heatmap."""
        data = simulation.soft_skills_data or {
            "professionalism": 70, "clarity": 70, "confidence": 70, "count": 0
        }
        
        count = data.get("count", 0)
        for skill in ["professionalism", "clarity", "confidence"]:
            current_avg = data.get(skill, 70)
            # Rolling average formula
            data[skill] = int(((current_avg * count) + new_scores[skill]) / (count + 1))
        
        data["count"] = count + 1
        simulation.soft_skills_data = data
        simulation.save()


class SummarizerAgent:
    pass
class TaskEvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(EVALUATION_MODELS + HEAVY_REASONING_MODELS)

    def evaluate(self, simulation, task, zip_file):
        # 1. Read the contents of the ZIP file
        file_contents = ""
        file_list = []
        wrong_format_detected = False
        try:
            with zipfile.ZipFile(zip_file) as z:
                for file_name in z.namelist():
                    if not file_name.endswith('/'): 
                        file_list.append(file_name)
                        if task.expected_file_extension and not any(f.endswith(task.expected_file_extension) for f in file_list):
                            wrong_format_detected = True
                        with z.open(file_name) as f:
                            file_contents += f"\n--- File: {file_name} ---\n"
                            # Handle potential binary data in CSVs/Models gracefully
                            file_contents += f.read().decode('utf-8', errors='ignore')[:5000] # Cap per file
        except Exception as e:
            return f"SCORE: 0 | FEEDBACK: Error reading ZIP: {str(e)}"
        if wrong_format_detected and task.expected_file_extension:
            return f"SCORE: 10 | FEEDBACK: You submitted the wrong file type. For this task, I expected a {task.expected_file_extension} file."
        # 2. Enhanced Prompt for AI/ML and Technical Projects
        prompt = f"""
        You are a Senior Technical Lead evaluating a candidate's submission.
        
        PROJECT CONTEXT:
        Role: {simulation.role_title}
        Project: {simulation.project_title}
        Current Task: {task.title}
        Task Instructions: {task.instruction}

        REFERENCE GOLD STANDARD (Perfect Answer):
        {simulation.expected_output_template}

        USER'S SUBMITTED FILES: {", ".join(file_list)}
        USER'S CODE CONTENT:
        {file_contents}

        EVALUATION CRITERIA:
        1. COMPLETENESS: Did the user provide the expected files (e.g., .py, .csv, .ipynb)?
        2. LOGIC: Does the code perform the requested task (e.g., data preprocessing, model training)?
        3. ACCURACY: How closely does the logic match the Reference Gold Standard?
        4. BEST PRACTICES: Usage of appropriate libraries (pandas, sklearn, etc.) and clean code.
        STRICT RULE: Only evaluate the user's work against the CURRENT task: {task.title}. 
        If they have old files from previous tasks in their ZIP, IGNORE them. 
        The feeback should be in second person.
        Focus only on: {task.instruction}.
        OUTPUT FORMAT (Strictly follow this):
        SCORE: [0-100] | FEEDBACK: [2-3 sentences explaining the grade]
        """
        
        return self._call_openrouter([{"role": "system", "content": prompt}])

# ============================================================
# PERFORMANCE AGENT (FINAL REPORT)
# ============================================================

class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(EVALUATION_MODELS + THINKING_MODELS)

    def generate_final_report(self, simulation):
        tasks = simulation.tasks.all().order_by('order') # [cite: 58]
        task_breakdown = []
        
        for task in tasks:
            # BUG FIX 3: Filter submissions strictly by the task instance
            latest_sub = task.submissions.all().order_by('-created_at').first()
            
            if not task.requires_submission:
                status = "Discussion-based"
                score = 100 if task.is_completed else 0
                feedback = "Instructional/Discussion task completed."
            elif latest_sub:
                status = "Completed"
                score = latest_sub.score
                feedback = latest_sub.feedback
            else:
                status = "Incomplete"
                score = 0
                feedback = "No submission recorded."

            task_breakdown.append({
                "title": task.title,
                "score": score,
                "feedback": feedback,
                "status": status
            })
        completed_tasks = simulation.tasks.filter(is_completed=True)
        task_summary = "\n".join([f"Task: {t.title} | Score: {t.score}" for t in completed_tasks])
        # 2. Gather global stats for the summary scores
        all_messages = Message.objects.filter(conversation__simulation=simulation).order_by('timestamp')
        chat_transcript = "\n".join([f"{m.sender}: {m.text}" for m in all_messages])

        prompt = f"""
        You are a Senior Career Coach. Analyze the overall simulation.
        Project: {simulation.project_title}
        Transcript: {chat_transcript}
        
        Technical Task Scores:
        {task_summary}

        Analyze the user's performance across these metrics:
        1. Communication (Tone, clarity, professionalism with HR/Peer/Client)
        2. Technical Competence (Based on scores and technical chat)
        3. Problem Solving (How they handled blockers mentioned in chat)
        4. Career Readiness (Overall fit for this specific role)
        5. Baased on the Users Preformance, tell the overall performace score out of 100

        Return a STRICT JSON object:
        {{
            "overall_performance": 0-100,
            "communication_score": 0-100,
            "technical_score": 0-100,
            "problem_solving_score": 0-100,
            "summary": "Detailed overall feedback...",
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."]
        }}
        """
        
        response_text = self._call_openrouter([{"role": "system", "content": prompt}])


        try:
            cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
            report_data = json.loads(cleaned_text)
            # 3. Attach the granular task breakdown to the final JSON
            report_data['task_breakdown'] = task_breakdown
            return report_data
        except:
            return {"summary": "Error", "task_breakdown": task_breakdown}




