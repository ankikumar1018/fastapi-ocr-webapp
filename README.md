# Real-Time OCR Processing Platform

This project is a web application that allows users to upload images and extract text from those images using Optical Character Recognition (OCR). It leverages FastAPI for the backend and includes real-time notifications via WebSocket to inform users about the upload and processing status.

## Features

- **Image Upload**: Users can upload image files through a simple web interface.
- **OCR Processing**: The application uses Tesseract to extract text from uploaded images.
- **Real-Time Notifications**: Users receive real-time updates about the upload and processing status.
- **Extracted Text Display**: The extracted text is displayed on the webpage once processing is complete.

## Technologies Used

- **Backend**: FastAPI
- **OCR Library**: Tesseract
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (optional for extended functionality)
- **WebSocket**: For real-time notifications
- **Containerization**: Docker

## Prerequisites

- Docker
- Docker Compose
- (Optional) PostgreSQL installed on your machine if you plan to use it directly instead of in Docker.

## Installation

### Using Docker

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ankikumar1018/fastapi-ocr-webapp.git
   cd <repository-directory>

2. **Build and run the Docker containers**:

   ```bash
   docker-compose up --build

3. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:8000/`.

### Without Docker (optional)

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>

2. **Create a virtual environment:**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install required packages**:

   ```bash
   pip install fastapi uvicorn python-multipart aiofiles pytesseract pillow psycopg2-binary websockets

4. **Install Tesseract**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>

4. **Install Tesseract**:
   - Follow the instructions for your operating system to install Tesseract.
   - Ensure Tesseract is added to your system's PATH.

## Running the Application

1. **Start the FastAPI server**:

   ```bash
   uvicorn app:app --reload
2. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:8000/`.

## Usage

1. Use the upload form to select an image file and click the "Upload" button.
2. Watch for real-time notifications that indicate the status of your upload and OCR processing.
3. After processing is complete, The extracted text will be displayed below the upload form.

## Optional: PostgreSQL Setup

To enable PostgreSQL storage for extracted data:

1. Install PostgreSQL on your machine.
2. Create a database and configure your connection in the FastAPI application (if implemented).
3. Modify the code to store the extracted text and metadata in the database.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Tesseract](https://github.com/tesseract-ocr/tesseract)
- [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for improvements or bugs.
