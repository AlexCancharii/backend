"""
Diccionario con los 30 ejercicios más comunes de gimnasio
y sus patrones de reconocimiento para el agente de fitness
"""

EJERCICIOS = {
    # Pecho
    'bench_press': r'bench|press|pecho|pectoral|press de banca',
    'incline_press': r'incline|inclinado|press inclinado',
    'decline_press': r'decline|declinado|press declinado',
    'chest_fly': r'fly|vuelo|aperturas|pec.?deck|pec deck|butterfly',
    'push_up': r'push.?up|flexion|flexiones|lagartijas',
    
    # Espalda
    'deadlift': r'deadlift|peso muerto|muerto',
    'pull_up': r'pull.?up|dominada|dominadas|chin.?up',
    'lat_pulldown': r'lat|pulldown|jalones|polea|jalón al pecho',
    'row': r'row|remo|remada',
    'back_extension': r'back extension|extension|hiperextensiones|lumbar',
    
    # Piernas
    'squat': r'squat|sentadilla|pierna',
    'leg_press': r'leg press|prensa|prensa de piernas',
    'leg_extension': r'leg extension|extension|extensiones|cuadriceps',
    'leg_curl': r'leg curl|curl|femoral|isquiotibiales',
    'calf_raise': r'calf|pantorrilla|gemelo|elevaciones|raise',
    'lunge': r'lunge|zancada|estocada',
    
    # Hombros
    'overhead_press': r'overhead|press|hombro|militar|press militar',
    'lateral_raise': r'lateral|raise|elevacion|elevaciones laterales',
    'front_raise': r'front|raise|elevaciones frontales',
    'face_pull': r'face pull|face|pull|jalones faciales',
    
    # Brazos
    'curl': r'curl|bicep|bíceps',
    'hammer_curl': r'hammer|martillo|curl martillo',
    'tricep_extension': r'tricep|extension|extensiones de triceps|triceps',
    'tricep_pushdown': r'pushdown|polea|triceps|push.?down',
    'dips': r'dips|fondos|paralelas',
    
    # Core
    'crunch': r'crunch|abdominal|abdominales|crunches',
    'plank': r'plank|plancha|tabla',
    'russian_twist': r'russian|twist|ruso|giros|twists',
    'leg_raise': r'leg raise|elevacion|elevaciones de pierna|raise',
    'mountain_climber': r'mountain|climber|escalador|escaladores'
} 