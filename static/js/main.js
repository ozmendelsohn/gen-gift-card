document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionnaireForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/generate-message', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.status === 'success' && data.preview_url) {
                window.location.href = data.preview_url;
            } else {
                alert('Failed to generate message: ' + (data.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the message');
        }
    });
});