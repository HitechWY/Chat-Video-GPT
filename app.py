import os
from flask import Flask, render_template, jsonify, request
import logging
from lumaai import LumaAI

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "your-secret-key"

LUMA_API_KEY = os.environ.get('LUMA_API_KEY')

# Initialize Luma client
client = LumaAI(auth_token=LUMA_API_KEY)

# Video style presets
VIDEO_STYLES = {
    'cinematic': {
        'prompt_prefix': 'Cinematic scene with dramatic lighting, professional camera movement, depth of field, and film grain:',
        'aspect_ratio': '21:9',
        'camera_motion': 'camera orbit slow'
    },
    'anime': {
        'prompt_prefix': 'Anime style animation with cel shading, vibrant colors, and dynamic composition in the style of high-quality Japanese animation:',
        'aspect_ratio': '16:9',
        'camera_motion': 'camera dolly in'
    },
    'realistic': {
        'prompt_prefix': 'Photorealistic scene with natural lighting, detailed textures, and physical accuracy:',
        'aspect_ratio': '16:9',
        'camera_motion': 'camera track right'
    },
    'artistic': {
        'prompt_prefix': 'Artistic interpretation with painterly effects, bold colors, and creative composition inspired by contemporary digital art:',
        'aspect_ratio': '16:9',
        'camera_motion': 'camera pan up'
    },
    'retro': {
        'prompt_prefix': 'Vintage-inspired scene with VHS effects, analog color grading, and nostalgic atmosphere from the 80s:',
        'aspect_ratio': '4:3',
        'camera_motion': 'camera zoom out'
    },
    'fantasy': {
        'prompt_prefix': 'Magical fantasy scene with ethereal lighting, particle effects, and enchanted atmosphere:',
        'aspect_ratio': '16:9',
        'camera_motion': 'camera orbit left'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    # Add sample prompts and their categories
    INSPIRATION_CATEGORIES = {
        'Nature': [
            'Serene waterfall in a lush forest with sunlight streaming through the trees',
            'Northern lights dancing across a starlit arctic sky',
            'Blooming cherry blossoms swaying in a gentle spring breeze'
        ],
        'Sci-Fi': [
            'Futuristic cityscape with flying vehicles and neon lights',
            'Space station orbiting a distant planet with multiple moons',
            'Cyberpunk street scene with holographic advertisements'
        ],
        'Fantasy': [
            'Ancient dragon soaring through misty mountains',
            'Magical forest with glowing butterflies and fairy lights',
            'Wizard\'s tower floating in the clouds at sunset'
        ],
        'Abstract': [
            'Swirling patterns of liquid colors forming geometric shapes',
            'Floating crystals refracting light in a void',
            'Morphing fractals with dynamic color transitions'
        ]
    }

    return render_template('gallery.html', categories=INSPIRATION_CATEGORIES)

@app.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        prompt = request.json.get('prompt')
        style = request.json.get('style', 'cinematic')  # Default to cinematic
        
        if not prompt:
            logger.error("No prompt provided in request")
            return jsonify({'error': 'Prompt is required'}), 400
            
        # Get style configuration
        style_config = VIDEO_STYLES.get(style, VIDEO_STYLES['cinematic'])
        
        # Combine style prefix with user prompt
        final_prompt = f"{style_config['prompt_prefix']} {prompt}"
        
        logger.info(f"Creating video generation with style {style} and prompt: {final_prompt}")
        # Add camera motion to the prompt for dynamic movement
        final_prompt = f"{final_prompt} {style_config.get('camera_motion', '')}"
        
        generation = client.generations.create(
            prompt=final_prompt,
            loop=True,
            aspect_ratio=style_config['aspect_ratio']
        )
        
        return jsonify({
            'video_id': generation.id,
            'status': 'pending'
        })
    except Exception as e:
        error_msg = f"Error generating video: {str(e)}"
        logger.error(error_msg)
        logger.exception("Full traceback:")
        return jsonify({'error': str(e)}), 500

@app.route('/video-status/<video_id>')
def video_status(video_id):
    try:
        if not LUMA_API_KEY:
            logger.error("LUMA_API_KEY is not set")
            return jsonify({'error': 'API key is not configured'}), 500

        logger.info(f"Checking status for video: {video_id}")
        try:
            generation = client.generations.get(id=video_id)
        except Exception as api_error:
            logger.error(f"Error from Luma API: {str(api_error)}")
            return jsonify({
                'status': 'error',
                'error': str(api_error)
            }), 500
        
        logger.info(f"Got video status: {generation.state}")
        
        # Map generation states to our status values
        status_mapping = {
            'completed': 'completed',
            'failed': 'failed',
            'dreaming': 'pending'
        }
        
        current_status = status_mapping.get(generation.state, 'pending')
        
        # Get video URL if available
        video_url = ''
        if hasattr(generation, 'assets') and generation.state == 'completed':
            video_url = generation.assets.video if generation.assets else ''
                
        # Get prompt from inputs if available
        prompt = generation.inputs.prompt if hasattr(generation, 'inputs') else ''

        return jsonify({
            'status': current_status,
            'url': video_url,
            'prompt': prompt
        })

    except Exception as e:
        error_msg = f"Error checking video status: {str(e)}"
        logger.error(error_msg)
        logger.exception("Full traceback:")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'details': error_msg
        }), 500

# Configuration at end of file removed since it's now in main.py