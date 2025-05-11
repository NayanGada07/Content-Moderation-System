document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadForm = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const previewImage = document.getElementById('preview-image');
    const nudityAlert = document.getElementById('nudity-alert');
    const nudityLevel = document.getElementById('nudity-level');
    const nudityDescription = document.getElementById('nudity-description');
    const nudityScoreBar = document.getElementById('nudity-score-bar');
    const nudityScoreValue = document.getElementById('nudity-score-value');
    const safeScoreBar = document.getElementById('safe-score-bar');
    const safeScoreValue = document.getElementById('safe-score-value');
    const sexyScoreBar = document.getElementById('sexy-score-bar');
    const sexyScoreValue = document.getElementById('sexy-score-value');
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if a file was selected
        if (!imageUpload.files.length) {
            showError('Please select an image to upload.');
            return;
        }
        
        // Check file type
        const file = imageUpload.files[0];
        const fileType = file.type;
        if (!fileType.match('image.*')) {
            showError('Please upload an image file.');
            return;
        }
        
        // Show loading state
        resetUI();
        loadingDiv.classList.remove('d-none');
        
        // Create form data for the API request
        const formData = new FormData();
        formData.append('image', file);
        
        // Send the request to the server
        fetch('/classify', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Server error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            loadingDiv.classList.add('d-none');
            displayResults(data);
        })
        .catch(error => {
            loadingDiv.classList.add('d-none');
            showError(error.message || 'An error occurred during image processing.');
        });
    });
    
    // Display the classification results
    function displayResults(data) {
        // Show the results container
        resultsDiv.classList.remove('d-none');
        
        // Set the image preview
        previewImage.src = `data:image/jpeg;base64,${data.image}`;
        
        // Update progress bars
        nudityScoreBar.style.width = `${data.nudity_score}%`;
        nudityScoreValue.textContent = `${data.nudity_score}%`;
        
        safeScoreBar.style.width = `${data.safe_score}%`;
        safeScoreValue.textContent = `${data.safe_score}%`;
        
        sexyScoreBar.style.width = `${data.sexy_score}%`;
        sexyScoreValue.textContent = `${data.sexy_score}%`;
        
        // Set alert style based on nudity level
        nudityLevel.textContent = `Nudity Level: ${data.nudity_level}`;
        
        // Customize alert based on nudity level
        const levelDescription = {
            'Safe': 'This image appears to be safe for general viewing.',
            'Low': 'This image contains minimal suggestive content.',
            'Moderate': 'This image contains moderate nudity or suggestive content.',
            'High': 'This image contains significant nudity content.',
            'Extreme': 'This image contains explicit nudity content.'
        };
        
        nudityDescription.textContent = levelDescription[data.nudity_level] || 
            'The image has been analyzed for nudity content.';
        
        // Set alert color based on nudity level
        nudityAlert.className = 'alert';
        switch (data.nudity_level) {
            case 'Safe':
                nudityAlert.classList.add('alert-success');
                break;
            case 'Low':
                nudityAlert.classList.add('alert-info');
                break;
            case 'Moderate':
                nudityAlert.classList.add('alert-warning');
                break;
            case 'High':
            case 'Extreme':
                nudityAlert.classList.add('alert-danger');
                break;
            default:
                nudityAlert.classList.add('alert-secondary');
        }
    }
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            errorAlert.classList.add('d-none');
        }, 5000);
    }
    
    // Reset UI state
    function resetUI() {
        resultsDiv.classList.add('d-none');
        errorAlert.classList.add('d-none');
        loadingDiv.classList.add('d-none');
    }
    
    // Show image preview when file is selected
    imageUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            resetUI();
        }
    });
});
