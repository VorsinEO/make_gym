import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config
import os
import logging
import json

# Set up logging
def setup_logging(config_data):
    """Configure logging based on config settings."""
    log_level = getattr(logging, config_data.get('log_level', 'INFO').upper())
    log_format = config_data.get('log_format', '%(asctime)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('workout_logger.log')
        ]
    )
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging(config.load_config())

# Set page config for mobile-first design
st.set_page_config(
    page_title="Workout Logger",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-first design
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .stTextInput>div>div>input {
        width: 100%;
    }
    .stNumberInput>div>div>input {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def load_history(filename):
    """Load workout history from CSV file."""
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            return {
                'workouts': sorted(df['workout_name'].unique().tolist()),
                'exercises': sorted(df['exercise_name'].unique().tolist()),
                'data': df
            }
        except Exception:
            return {'workouts': [], 'exercises': [], 'data': pd.DataFrame()}
    return {'workouts': [], 'exercises': [], 'data': pd.DataFrame()}

def get_exercise_history(df, exercise_name):
    """Get the last two workouts for a specific exercise."""
    if df.empty:
        return None
    
    # Filter for the exercise and sort by timestamp
    exercise_data = df[df['exercise_name'] == exercise_name].sort_values('timestamp', ascending=False)
    
    if exercise_data.empty:
        return None
    
    # Convert timestamp to datetime
    exercise_data['timestamp'] = pd.to_datetime(exercise_data['timestamp'])
    
    # Get unique workout dates
    workout_dates = exercise_data['timestamp'].dt.date.unique()
    
    history = []
    for date in workout_dates[:2]:  # Get last two workouts
        workout_data = exercise_data[exercise_data['timestamp'].dt.date == date]
        sets = []
        for _, row in workout_data.iterrows():
            sets.append({
                'set': row['set_number'],
                'weight': row['weight_kg'],
                'reps': row['reps']
            })
        history.append({
            'date': date.strftime('%Y-%m-%d'),
            'sets': sorted(sets, key=lambda x: x['set'])
        })
    
    return history

def save_to_csv(data, filename):
    """Save workout data to CSV file."""
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

def send_to_webhook(data, webhook_url):
    """Send workout data to webhook."""
    try:
        logger.info(f"Attempting to send data to webhook: {webhook_url}")
        logger.debug(f"Data payload: {json.dumps(data, indent=2)}")
        
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        
        logger.info(f"Successfully sent data to webhook. Status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to webhook: {str(e)}")
        if hasattr(e.response, 'text'):
            logger.error(f"Error response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while sending data to webhook: {str(e)}")
        return False

def get_workout_form():
    """Display and handle the workout form."""
    config_data = config.load_config()
    
    # Initialize session state for form data if not exists
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Initialize current exercise tracking if not exists
    if 'current_exercise' not in st.session_state:
        st.session_state.current_exercise = None
    if 'set_count' not in st.session_state:
        st.session_state.set_count = 1  # Initialize to 1 instead of 0
    if 'last_exercise' not in st.session_state:
        st.session_state.last_exercise = None
    if 'last_workout' not in st.session_state:
        st.session_state.last_workout = None
    
    # Load history for dropdowns
    history = load_history(config_data['local_file'])
    
    # Required fields
    for field in config_data['required_fields']:
        if field == 'set_number':
            current_exercise = st.session_state.form_data.get('exercise_name')
            current_workout = st.session_state.form_data.get('workout_name')
            
            # Reset set count if exercise changed or workout changed
            if (current_exercise != st.session_state.last_exercise or 
                current_workout != st.session_state.last_workout):
                st.session_state.set_count = 1
                st.session_state.last_exercise = current_exercise
                st.session_state.last_workout = current_workout
            
            # Ensure set_count is at least 1
            current_set_count = max(1, st.session_state.set_count)
            st.session_state.form_data[field] = st.number_input(
                "Set Number", 
                min_value=1, 
                value=current_set_count,
                disabled=True  # Auto-managed
            )
        elif field == 'workout_name':
            # Create two columns for workout name selection
            col1, col2 = st.columns([3, 1])
            with col1:
                # Always show the selectbox, even if no history
                options = ["New Workout"]
                if history['workouts']:
                    options.extend(history['workouts'])
                
                st.session_state.form_data[field] = st.selectbox(
                    "Select Workout",
                    options,
                    format_func=lambda x: "New Workout" if x == "New Workout" else x
                )
            with col2:
                if st.session_state.form_data.get(field) == "New Workout":
                    st.session_state.form_data[field] = st.text_input(
                        "Enter New Workout Name",
                        key="new_workout"
                    )
        elif field == 'exercise_name':
            # Create two columns for exercise name selection
            col1, col2 = st.columns([3, 1])
            with col1:
                # Always show the selectbox, even if no history
                options = ["New Exercise"]
                if history['exercises']:
                    options.extend(history['exercises'])
                
                st.session_state.form_data[field] = st.selectbox(
                    "Select Exercise",
                    options,
                    format_func=lambda x: "New Exercise" if x == "New Exercise" else x
                )
            with col2:
                if st.session_state.form_data.get(field) == "New Exercise":
                    st.session_state.form_data[field] = st.text_input(
                        "Enter New Exercise Name",
                        key="new_exercise"
                    )
            
            # Show exercise history if an existing exercise is selected
            if (st.session_state.form_data.get(field) and 
                st.session_state.form_data[field] != "New Exercise" and 
                st.session_state.form_data[field] in history['exercises']):
                
                exercise_history = get_exercise_history(history['data'], st.session_state.form_data[field])
                if exercise_history:
                    with st.expander("📊 Exercise History"):
                        for workout in exercise_history:
                            st.write(f"**Date:** {workout['date']}")
                            for set_data in workout['sets']:
                                st.write(f"Set {set_data['set']}: {set_data['weight']}kg × {set_data['reps']} reps")
                            st.markdown("---")
        elif field == 'weight_kg':
            st.session_state.form_data[field] = st.number_input(
                "Weight (kg)", min_value=0.0, value=0.0, step=0.5
            )
        elif field == 'reps':
            st.session_state.form_data[field] = st.number_input(
                "Reps", min_value=1, value=1
            )
    
    # Optional fields
    for field in config_data['optional_fields']:
        if field == 'rpe':
            st.session_state.form_data[field] = st.number_input(
                "RPE (Rate of Perceived Exertion)", 
                min_value=1, max_value=10, value=7
            )
        elif field == 'rest_sec':
            st.session_state.form_data[field] = st.number_input(
                "Rest Time (seconds)", min_value=0, value=60
            )
        else:
            st.session_state.form_data[field] = st.text_area(
                field.replace('_', ' ').title()
            )
    
    # Add timestamp
    st.session_state.form_data['timestamp'] = datetime.now().isoformat()
    
    return st.session_state.form_data

def main():
    logger.info("Starting Workout Logger application")
    st.title("💪 Workout Logger")
    
    # Mode selection
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    
    if st.session_state.mode is None:
        logger.debug("No mode selected yet, showing mode selection buttons")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Web Mode", use_container_width=True):
                st.session_state.mode = "web"
                logger.info("User selected Web Mode")
        with col2:
            if st.button("Local Mode", use_container_width=True):
                st.session_state.mode = "local"
                logger.info("User selected Local Mode")
    
    if st.session_state.mode:
        logger.info(f"Application running in {st.session_state.mode.title()} Mode")
        st.write(f"Current Mode: {st.session_state.mode.title()}")
        
        # Initialize workout state if not exists
        if 'workout_active' not in st.session_state:
            st.session_state.workout_active = False
        if 'current_workout' not in st.session_state:
            st.session_state.current_workout = None
        
        if not st.session_state.workout_active:
            if st.button("Start New Workout", use_container_width=True):
                st.session_state.workout_active = True
                st.session_state.form_data = {}
                st.session_state.current_exercise = None
                st.session_state.set_count = 1  # Initialize to 1 instead of 0
                st.session_state.last_exercise = None
                st.session_state.last_workout = None
                st.rerun()
        
        if st.session_state.workout_active:
            st.subheader("Log Exercise")
            form_data = get_workout_form()
            
            # Show current workout status
            if form_data.get('workout_name'):
                st.info(f"Current Workout: {form_data['workout_name']}")
                if form_data.get('exercise_name'):
                    st.info(f"Current Exercise: {form_data['exercise_name']} - Set {form_data['set_number']}")
            
            # Save button
            if st.button("Save Set", use_container_width=True):
                config_data = config.load_config()
                
                # Save to CSV regardless of mode
                save_to_csv(form_data, config_data['local_file'])
                
                # Send to webhook if in web mode
                if st.session_state.mode == "web":
                    if send_to_webhook(form_data, config_data['webhook_url']):
                        st.success("Set saved and sent to webhook!")
                    else:
                        st.error("Failed to send data to webhook")
                else:
                    st.success("Set saved locally!")
                
                # Increment set count after saving
                st.session_state.set_count += 1
                
                # Clear form data but keep workout and exercise context
                workout_name = form_data.get('workout_name')
                exercise_name = form_data.get('exercise_name')
                st.session_state.form_data = {
                    'workout_name': workout_name,
                    'exercise_name': exercise_name
                }
                st.rerun()
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("New Exercise", use_container_width=True):
                    st.session_state.form_data = {
                        'workout_name': form_data.get('workout_name')
                    }
                    st.session_state.current_exercise = None
                    st.session_state.set_count = 1
                    st.session_state.last_exercise = None
                    st.session_state.last_workout = None
                    st.rerun()
            with col2:
                if st.button("End Workout", use_container_width=True):
                    st.session_state.workout_active = False
                    st.session_state.current_exercise = None
                    st.session_state.set_count = 1
                    st.session_state.last_exercise = None
                    st.session_state.last_workout = None
                    st.rerun()

if __name__ == "__main__":
    main() 