
import streamlit as st
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import StringIO
import random
import math

def load_mission(file):
    content = json.load(file)
    return content

def generate_simulated_drones(num_drones=50):
    drones = []
    for i in range(num_drones):
        segments = []
        for t in range(0, 15, 3):
            x = random.randint(0, 12)
            y = random.randint(0, 12)
            segments.append({"coords": [x, y], "time": t})
        drones.append({"id": f"drone{i+1}", "segments": segments})
    return drones

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def is_spatial_conflict(p_seg, o_seg, threshold=2):
    return distance(p_seg['coords'], o_seg['coords']) < threshold

def is_temporal_overlap(t1, t2, margin=1):
    return abs(t1 - t2) <= margin

def check_conflicts(primary, others):
    conflicts = []
    for other in others:
        for p_seg in primary['segments']:
            for o_seg in other['segments']:
                if is_spatial_conflict(p_seg, o_seg) and is_temporal_overlap(p_seg['time'], o_seg['time']):
                    conflicts.append({
                        'location': p_seg['coords'],
                        'time': p_seg['time'],
                        'conflict_with': other['id']
                    })
    return ("conflict detected", conflicts) if conflicts else ("clear", [])

st.title("🛩️ UAV Deconfliction Checker")

uploaded_file = st.file_uploader("Upload Primary Drone JSON", type="json")

if uploaded_file:
    primary = load_mission(uploaded_file)
    others = generate_simulated_drones()

    status, details = check_conflicts(primary, others)
    st.subheader(f"Status: {status}")

    if details:
        for d in details:
            st.warning(f"Conflict with {d['conflict_with']} at {d['location']} around t={d['time']}")

    # Visualization
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    def extract_coords(drone):
        x = [p['coords'][0] for p in drone['segments']]
        y = [p['coords'][1] for p in drone['segments']]
        z = [p['time'] for p in drone['segments']]
        return x, y, z

    px, py, pz = extract_coords(primary)
    ax.plot(px, py, pz, 'b-o', label='Primary Drone')

    for other in others[:10]:
        ox, oy, oz = extract_coords(other)
        ax.plot(ox, oy, oz, 'g--x', alpha=0.5)

    for c in details:
        ax.scatter(c['location'][0], c['location'][1], c['time'], c='r', s=50)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Time")
    ax.set_title("3D Visualization of Conflicts")
    st.pyplot(fig)
