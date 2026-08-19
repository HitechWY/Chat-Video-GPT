class VideoAPI {
    async generateVideo(prompt, style) {
        try {
            const response = await fetch('/generate-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt, style }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate video');
            }

            return data;
        } catch (error) {
            console.error('Error generating video:', error);
            throw error;
        }
    }

    async checkVideoStatus(videoId) {
        try {
            const response = await fetch(`/video-status/${videoId}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || data.details || 'Failed to check video status');
            }
            
            return data;
        } catch (error) {
            console.error('Error checking video status:', error);
            throw error;
        }
    }
}