import pytest
import pandas as pd
import os
import json
from unittest.mock import patch, MagicMock
import app
import config
import logging

@pytest.fixture
def sample_workout_data():
    return {
        'workout_name': 'Test Workout',
        'exercise_name': 'Test Exercise',
        'set_number': 1,
        'weight_kg': 100.0,
        'reps': 10,
        'rpe': 8,
        'rest_sec': 60,
        'notes': 'Test notes',
        'timestamp': '2024-01-01T00:00:00'
    }

@pytest.fixture
def mock_config():
    return {
        'webhook_url': 'https://test.webhook.url',
        'local_file': 'test_training_log.csv',
        'required_fields': ['workout_name', 'exercise_name', 'set_number', 'weight_kg', 'reps'],
        'optional_fields': ['rpe', 'rest_sec', 'notes'],
        'log_level': 'DEBUG',
        'log_format': '%(asctime)s - %(levelname)s - %(message)s'
    }

def test_save_to_csv(sample_workout_data, mock_config):
    with patch('app.config.load_config', return_value=mock_config):
        # Test saving to CSV
        app.save_to_csv(sample_workout_data, mock_config['local_file'])
        
        # Verify file exists and contains correct data
        assert os.path.exists(mock_config['local_file'])
        df = pd.read_csv(mock_config['local_file'])
        assert len(df) == 1
        assert df.iloc[0]['workout_name'] == sample_workout_data['workout_name']
        assert df.iloc[0]['exercise_name'] == sample_workout_data['exercise_name']
        
        # Clean up
        os.remove(mock_config['local_file'])

def test_send_to_webhook_success(sample_workout_data, mock_config):
    with patch('app.config.load_config', return_value=mock_config), \
         patch('requests.post') as mock_post:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'Success'
        mock_post.return_value = mock_response
        
        # Test webhook sending
        result = app.send_to_webhook(sample_workout_data, mock_config['webhook_url'])
        
        # Verify success
        assert result is True
        mock_post.assert_called_once_with(
            mock_config['webhook_url'],
            json=sample_workout_data
        )

def test_send_to_webhook_failure(sample_workout_data, mock_config):
    with patch('app.config.load_config', return_value=mock_config), \
         patch('requests.post') as mock_post:
        # Mock failed response
        mock_post.side_effect = Exception('Connection error')
        
        # Test webhook sending
        result = app.send_to_webhook(sample_workout_data, mock_config['webhook_url'])
        
        # Verify failure
        assert result is False

def test_load_history(mock_config):
    with patch('app.config.load_config', return_value=mock_config):
        # Create test data
        test_data = pd.DataFrame([
            {
                'workout_name': 'Workout 1',
                'exercise_name': 'Exercise 1',
                'set_number': 1,
                'weight_kg': 100.0,
                'reps': 10
            }
        ])
        test_data.to_csv(mock_config['local_file'], index=False)
        
        # Test loading history
        history = app.load_history(mock_config['local_file'])
        
        # Verify history structure
        assert 'workouts' in history
        assert 'exercises' in history
        assert 'data' in history
        assert len(history['workouts']) == 1
        assert len(history['exercises']) == 1
        
        # Clean up
        os.remove(mock_config['local_file'])

def test_get_exercise_history(mock_config):
    with patch('app.config.load_config', return_value=mock_config):
        # Create test data with multiple sets
        test_data = pd.DataFrame([
            {
                'workout_name': 'Workout 1',
                'exercise_name': 'Exercise 1',
                'set_number': 1,
                'weight_kg': 100.0,
                'reps': 10,
                'timestamp': '2024-01-01T00:00:00'
            },
            {
                'workout_name': 'Workout 1',
                'exercise_name': 'Exercise 1',
                'set_number': 2,
                'weight_kg': 105.0,
                'reps': 8,
                'timestamp': '2024-01-01T00:00:00'
            }
        ])
        test_data.to_csv(mock_config['local_file'], index=False)
        
        # Test getting exercise history
        history = app.get_exercise_history(test_data, 'Exercise 1')
        
        # Verify history structure
        assert len(history) == 1  # One workout
        assert len(history[0]['sets']) == 2  # Two sets
        assert history[0]['sets'][0]['weight'] == 100.0
        assert history[0]['sets'][1]['weight'] == 105.0
        
        # Clean up
        os.remove(mock_config['local_file'])

def test_setup_logging(mock_config):
    with patch('app.config.load_config', return_value=mock_config):
        # Test logging setup
        logger = app.setup_logging(mock_config)
        
        # Verify logger is configured
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 2  # Stream and file handlers

if __name__ == '__main__':
    pytest.main([__file__]) 