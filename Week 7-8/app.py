from flask import Flask, render_template, jsonify, send_from_directory
import os
import random
from prediction_engine import PredictionEngine
from visualization import Visualizer

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "Week 5-6", "LSTM Model", "lstm_energy_model.h5")
DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "Week 1-2", "Ready For Feature Eng dataset", "cleaned_energy_consumption_data.csv")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")

# Initialize Engine and Visualizer
engine = PredictionEngine(MODEL_PATH, DATA_PATH)
visualizer = Visualizer(DATA_PATH, IMAGES_DIR)

@app.route('/')
def dashboard():
    # Update charts on page load
    visualizer.generate_all_charts()
    return render_template('index.html')

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    # In a real app, this would take user input. 
    # For demo, we use the last 24 values from the dataset.
    df = visualizer.df
    last_24 = df.sort_values('Timestamp').tail(24)['energy'].tolist()
    
    try:
        prediction = engine.predict_next_hour(last_24)
        return jsonify({
            'status': 'success',
            'prediction': round(prediction, 3),
            'unit': 'kWh'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    tips = [
        "Unplug devices that aren't in use to avoid phantom energy drain.",
        "Switch to LED bulbs to reduce lighting energy consumption by up to 75%.",
        "Wash clothes in cold water to save on water heating costs.",
        "Set your thermostat a few degrees lower in winter and higher in summer.",
        "Use a smart power strip to automatically turn off peripheral devices.",
        "Properly insulate your home to maintain temperature and reduce HVAC usage."
    ]
    # Return 3 random tips
    return jsonify({
        'status': 'success',
        'suggestions': random.sample(tips, 3)
    })

@app.route('/api/data', methods=['GET'])
def get_chart_data():
    df = visualizer.df
    # Hourly data (Last 24 hours)
    recent_24 = df.sort_values('Timestamp').tail(24)
    hourly_labels = recent_24['Timestamp'].dt.strftime('%H:%M').tolist()
    hourly_values = recent_24['energy'].tolist()

    # Daily data (Last 7 days)
    daily = df.groupby(df['Timestamp'].dt.date)['energy'].sum().tail(7)
    daily_labels = [d.strftime('%Y-%m-%d') for d in daily.index]
    daily_values = daily.tolist()

    # Device data
    device_usage = df.groupby('Appliance Type')['energy'].sum()
    device_labels = device_usage.index.tolist()
    device_values = device_usage.tolist()

    return jsonify({
        'hourly': {'labels': hourly_labels, 'values': hourly_values},
        'daily': {'labels': daily_labels, 'values': daily_values},
        'devices': {'labels': device_labels, 'values': device_values}
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    df = visualizer.df
    total_consumption = df['energy'].sum()
    avg_hourly = df['energy'].mean()
    max_usage = df['energy'].max()
    
    return jsonify({
        'total_consumption': round(total_consumption, 2),
        'avg_hourly': round(avg_hourly, 2),
        'max_usage': round(max_usage, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
