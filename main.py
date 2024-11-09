<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Classification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background-color: #f4f4f9;
            margin: 0;
        }
        h1 {
            color: #333;
        }
        input[type="file"] {
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #result {
            margin-top: 20px;
            font-size: 18px;
            text-align: center;
        }
        #uploadedImage {
            margin-top: 20px;
            max-width: 400px;
            height: auto;
            display: none;
            border: 2px solid #ddd;
            border-radius: 10px;
        }
    </style>
</head>
<body>

<h1>Weather Image Classification</h1>
<p>Upload an image to classify weather.</p>
<input type="file" id="fileInput" accept="image/*" onchange="previewImage(event)">
<br>
<img id="uploadedImage" src="" alt="Uploaded Image Preview" />
<br>
<button onclick="uploadImage()">Classify Image</button>

<div id="result"></div>

<script>
    function previewImage(event) {
        const reader = new FileReader();
        const imageField = document.getElementById('uploadedImage');

        reader.onload = function() {
            if (reader.readyState === 2) {
                imageField.src = reader.result;
                imageField.style.display = 'block';  
            }
        }
        reader.readAsDataURL(event.target.files[0]);
    }

    async function uploadImage() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select an image to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('result').innerHTML = `
                <p>Predicted Class: <strong>${result.predicted_class}</strong></p>
                <p>Prediction Confidence: ${result.prediction}</p>
            `;
        } else {
            document.getElementById('result').innerText = 'Error in classification. Please try again.';
        }
    }
</script>

</body>
</html>
