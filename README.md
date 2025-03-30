# Workout Logger

A mobile-first Streamlit web application for logging workouts, supporting both local storage and webhook integration.

## Features

- 📱 Mobile-first design
- 💾 Local storage (CSV) and webhook integration
- 📊 Exercise history tracking
- 🔄 Auto-incrementing set numbers
- 📝 Optional fields (RPE, rest time, notes)
- 🔍 Smart workout and exercise name suggestions
- 📈 Exercise history visualization

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd workout-logger
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses a `config.yaml` file for configuration. A default configuration will be created on first run. You can modify the following settings:

- `webhook_url`: URL for webhook integration
- `local_file`: Path to the CSV file for local storage
- `required_fields`: List of required fields for workout logging
- `optional_fields`: List of optional fields
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_format`: Format string for log messages

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Choose your mode:
   - **Local Mode**: Data is saved to a CSV file
   - **Web Mode**: Data is sent to the configured webhook

3. Start a new workout and log your exercises:
   - Select or create a workout name
   - Select or create an exercise name
   - Enter weight and reps
   - Add optional information (RPE, rest time, notes)
   - Save each set
   - Start a new exercise or end the workout

## Development

### Running Tests

```bash
python -m pytest test_app.py
```

### Logging

The application logs to both console and file (`workout_logger.log`). Log level can be configured in `config.yaml`.

## Project Structure

```
workout-logger/
├── app.py              # Main application
├── config.py           # Configuration management
├── test_app.py         # Unit tests
├── requirements.txt    # Python dependencies
├── config.yaml         # Application configuration
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 