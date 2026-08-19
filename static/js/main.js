// Helper Functions
function createVideoGrid() {
    const grid = document.createElement('div');
    grid.className = 'video-grid';
    document.querySelector('.generator-container').appendChild(grid);
    return grid;
}

function createVideoCard(videoUrl, prompt, style) {
    const card = document.createElement('div');
    card.className = 'video-card slide-up';
    
    const video = document.createElement('video');
    video.src = videoUrl;
    video.controls = true;
    video.loop = true;
    video.muted = true;
    
    const info = document.createElement('div');
    info.className = 'video-info';
    
    const promptText = document.createElement('p');
    promptText.className = 'prompt';
    promptText.textContent = prompt;
    
    const styleBadge = document.createElement('span');
    styleBadge.className = 'style-badge';
    styleBadge.textContent = style;
    
    info.appendChild(promptText);
    info.appendChild(styleBadge);
    
    card.appendChild(video);
    card.appendChild(info);
    
    return card;
}

document.addEventListener('DOMContentLoaded', () => {
    const api = new VideoAPI();
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt-input');
    const loadingOverlay = document.getElementById('loading-overlay');
    let timerInterval = null;

    // Initialize GSAP
    gsap.config({
        nullTargetWarn: false
    });

    function showGenerator() {
        document.querySelector('.landing-page').classList.add('hidden');
        document.getElementById('generator').classList.remove('hidden');
    }

    function startGenerationTimer() {
        const timerElement = document.getElementById('generation-timer');
        let seconds = 0;
        
        timerInterval = setInterval(() => {
            seconds++;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            timerElement.textContent = `Time elapsed: ${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    function stopGenerationTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function showError(message, duration = 5000) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message fade-in';
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '20px';
        errorDiv.style.right = '20px';
        errorDiv.style.backgroundColor = '#ff4444';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '1rem';
        errorDiv.style.borderRadius = '8px';
        errorDiv.style.zIndex = '1000';
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        gsap.to(errorDiv, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            delay: duration / 1000 - 0.5,
            onComplete: () => errorDiv.remove()
        });
    }

    async function monitorVideoGeneration(videoId, originalPrompt, style) {
        const maxAttempts = 60; // 5 minutes with 5-second intervals
        let attempts = 0;
        
        const checkInterval = setInterval(async () => {
            try {
                const status = await api.checkVideoStatus(videoId);
                
                if (status.status === 'completed') {
                    clearInterval(checkInterval);
                    stopGenerationTimer();
                    loadingOverlay.classList.add('hidden');
                    // Create video container
                    const videoGrid = document.querySelector('.video-grid') || createVideoGrid();
                    const videoCard = createVideoCard(status.url, status.prompt || originalPrompt, style);
                    videoGrid.insertBefore(videoCard, videoGrid.firstChild);
                    
                    // Open in new tab as well
                    window.open(status.url, '_blank');
                } else if (status.status === 'failed' || status.status === 'error') {
                    clearInterval(checkInterval);
                    stopGenerationTimer();
                    loadingOverlay.classList.add('hidden');
                    showError(status.error || 'Video generation failed. Please try again.');
                } else if (attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    stopGenerationTimer();
                    loadingOverlay.classList.add('hidden');
                    showError('Video generation timed out. Please try again.');
                }
                attempts++;
            } catch (error) {
                console.error("Error checking video status:", error);
                clearInterval(checkInterval);
                stopGenerationTimer();
                loadingOverlay.classList.add('hidden');
                showError('Failed to check video status. Please try again.');
            }
        }, 5000);
    }

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const style = document.getElementById('style-select').value;
        
        if (!prompt) {
            showError('Please enter a prompt');
            return;
        }

        try {
            loadingOverlay.classList.remove('hidden');
            startGenerationTimer();
            const response = await api.generateVideo(prompt, style);
            
            if (response.error) {
                throw new Error(response.error);
            }

            const videoId = response.video_id;
            await monitorVideoGeneration(videoId, prompt, style);
            
            promptInput.value = '';
        } catch (error) {
            showError(`Failed to generate video: ${error.message}`);
            loadingOverlay.classList.add('hidden');
            stopGenerationTimer();
        }
    });

    // Add enter key support for input
    promptInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            generateBtn.click();
        }
    });

    // Expose functions globally
    window.showGenerator = showGenerator;
});
