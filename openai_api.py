import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIAPI:
    def __init__(self):
        """Initialize the OpenAI API connection"""
        try:
            # Get API key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                print("Error: OPENAI_API_KEY not found in environment variables")
                self.connected = False
                return
                
            # Initialize OpenAI client using the newer client version
            self.client = openai.OpenAI(api_key=api_key)
            self.connected = True
            print("OpenAI API successfully connected")
        except Exception as e:
            print(f"Error initializing OpenAI API: {str(e)}")
            self.connected = False
            
    def is_connected(self):
        """Check if API connection is established"""
        return self.connected
    
    def generate_analysis(self, video_data):
        """
        Generate a detailed analysis report for a TikTok video
        
        Args:
            video_data (dict): Dictionary containing video metrics and details
            
        Returns:
            str: The generated analysis report
        """
        try:
            # Prepare the prompt with video data
            prompt = self._create_prompt(video_data)
            
            # Call OpenAI API using the newer client version
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert TikTok content strategist, data analyst, and viral growth consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Extract and return the response text using the new response format
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating analysis: {str(e)}")
            return f"Error generating analysis: {str(e)}"
            
    def _create_prompt(self, video_data):
        """Create a detailed prompt for the OpenAI API"""
        # Use the sheet's actual column names
        views_to_like = video_data.get('Views to Like Ratio (%)', video_data.get('Like-to-View Ratio (%)', 'N/A'))
        views_to_comment = video_data.get('Views to Comment Ratio (%)', video_data.get('Comment-to-View Ratio (%)', 'N/A'))
        views_to_save = video_data.get('Views to Save Ratio (%)', video_data.get('Save-to-View Ratio (%)', 'N/A'))
        like_to_comment = video_data.get('Like to Comment Ratio (%)', video_data.get('Comment-to-Like Ratio (%)', 'N/A'))
        like_to_save = video_data.get('Like to Save Ratio (%)', video_data.get('Save-to-Like Ratio (%)', 'N/A'))
        
        prompt = f"""
        SYSTEM ROLE:
        You are an expert TikTok content strategist, data analyst, and viral growth consultant.
        Your job is to deeply analyze the performance of each TikTok video based on provided performance data and storytelling structure.
        Your analysis must be specific, reflective, and actionable — focused on improving future content to maximize virality.

        DATA PROVIDED:

        Title: {video_data.get('Title', 'N/A')}

        Hook: {video_data.get('Hook', 'N/A')}

        Caption: {video_data.get('Caption', 'N/A')}

        Hashtags: {video_data.get('Hashtags', 'N/A')}

        Views: {video_data.get('Views', 'N/A')}

        Likes: {video_data.get('Likes', 'N/A')}

        Comments: {video_data.get('Comments', 'N/A')}

        Saves: {video_data.get('Saves', 'N/A')}

        Views to Like Ratio (%): {views_to_like}

        Views to Comment Ratio (%): {views_to_comment}

        Views to Save Ratio (%): {views_to_save}

        Like to Comment Ratio (%): {like_to_comment}

        Like to Save Ratio (%): {like_to_save}

        TASK:

        Carefully review each metric individually and explain:

        What the metric reveals about the video

        Why it performed well or poorly

        Emotional or psychological causes if relevant

        Storytelling structure or hook/caption influence if relevant

        Analyze metrics collectively:

        Cross-reference patterns between metrics

        Identify contradictions (e.g., good likes but poor saves = surface-level content)

        Detect whether audience resonance was emotional, intellectual, practical, or missing

        FINAL REPORT STRUCTURE:

        1. Overview Summary
        Write a human-like paragraph summarizing how the video performed overall — strengths, weaknesses, general vibe.

        2. Detailed Metric Breakdown
        For each metric (Views to Like, Views to Comment, Views to Save, Like to Comment, Like to Save):

        What does the metric reveal?

        Why is it good or bad based on TikTok audience psychology?

        How does it affect virality potential?

        3. Strengths Identified
        List what worked well (hook type, emotional tension, storytelling, topic choice, thumbnail if applicable)

        Link each strength back to its impact on engagement or retention

        4. Weaknesses Identified
        List where the video fell short (hook weakness, caption issues, emotional flatness, bad pacing, etc.)

        Explain WHY these weaknesses likely caused performance issues

        5. Actionable Improvements
        Specific, tactical advice for the next videos

        Focus especially on improving hook emotionality, storytelling structure, pacing, and memorability

        6. Viral Potential Score (Optional)
        Score the video 0–10 based on current performance indicators and storytelling power.

        Briefly explain your score.

        RULES YOU MUST FOLLOW:

        Be brutally honest if the video is weak. No fake positivity.

        Always back up claims with logical explanation.

        Do not offer vague advice ("make it better"); be specific ("add an emotional confrontation in first 2 seconds").

        Always connect analysis back to goal: helping the creator achieve virality through emotional connection, higher retention, saves, and shares.

        Keep language human, friendly but expert — no robotic summaries.
        
        ADDITIONAL ANALYSIS RULES TO FOLLOW:

        If Views to Like Ratio > 6%, recognize strong initial resonance.

        If Likes are high but Comments/Saves are low, describe the video as "surface-level resonance" — visually pleasing but not deeply emotional.

        If the topic is emotionally powerful (e.g., prayer, suffering, love, loss), critique execution, not topic choice, if performance is weak.

        Always recommend specific, tactical improvements (not vague advice) — suggest exact hook types, emotional techniques, or ending strategies.

        Score each video dynamically:
        - Strong Likes = Good base
        - Strong Comments = Emotional success
        - Strong Saves = Long-term memory creation
        - Lack of all three = Very low viral score

        Always tie all analysis back to the goal: Maximizing virality through emotional connection, high retention, and rewatch value.
        
        ADDITIONAL CONTENT IMPROVEMENT RULES:

        Carefully evaluate the caption:
        - If the caption is weak, generic, or lacks emotional pull, explain why it's weak.
        - Then suggest a stronger alternative caption that would emotionally resonate more or increase curiosity.

        Carefully evaluate the hashtags:
        - If the hashtags are too broad, irrelevant, or weak for virality, explain why.
        - Then suggest a better set of 3–5 hashtags that would:
          - Target the right audience
          - Increase discoverability
          - Stay niche enough to reach emotionally connected viewers.

        All caption and hashtag suggestions must be tailored to the topic and emotional tone of the video — no random or unrelated recommendations.
        """
        
        return prompt 