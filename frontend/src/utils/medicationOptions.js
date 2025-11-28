// Common medications database
export const COMMON_MEDICATIONS = [
  // Cardiovascular
  { value: 'Amlodipine', label: 'Amlodipine', category: 'Blood Pressure' },
  { value: 'Atorvastatin', label: 'Atorvastatin', category: 'Cholesterol' },
  { value: 'Lisinopril', label: 'Lisinopril', category: 'Blood Pressure' },
  { value: 'Metoprolol', label: 'Metoprolol', category: 'Blood Pressure' },
  { value: 'Losartan', label: 'Losartan', category: 'Blood Pressure' },
  { value: 'Simvastatin', label: 'Simvastatin', category: 'Cholesterol' },
  { value: 'Warfarin', label: 'Warfarin', category: 'Blood Thinner' },
  { value: 'Aspirin', label: 'Aspirin', category: 'Blood Thinner' },
  { value: 'Clopidogrel', label: 'Clopidogrel', category: 'Blood Thinner' },
  
  // Diabetes
  { value: 'Metformin', label: 'Metformin', category: 'Diabetes' },
  { value: 'Insulin', label: 'Insulin', category: 'Diabetes' },
  { value: 'Glipizide', label: 'Glipizide', category: 'Diabetes' },
  { value: 'Glyburide', label: 'Glyburide', category: 'Diabetes' },
  
  // Gastrointestinal
  { value: 'Omeprazole', label: 'Omeprazole', category: 'Stomach' },
  { value: 'Pantoprazole', label: 'Pantoprazole', category: 'Stomach' },
  { value: 'Esomeprazole', label: 'Esomeprazole', category: 'Stomach' },
  { value: 'Ranitidine', label: 'Ranitidine', category: 'Stomach' },
  
  // Mental Health
  { value: 'Sertraline', label: 'Sertraline', category: 'Antidepressant' },
  { value: 'Citalopram', label: 'Citalopram', category: 'Antidepressant' },
  { value: 'Escitalopram', label: 'Escitalopram', category: 'Antidepressant' },
  { value: 'Paroxetine', label: 'Paroxetine', category: 'Antidepressant' },
  { value: 'Fluoxetine', label: 'Fluoxetine', category: 'Antidepressant' },
  { value: 'Venlafaxine', label: 'Venlafaxine', category: 'Antidepressant' },
  { value: 'Duloxetine', label: 'Duloxetine', category: 'Antidepressant' },
  
  // Benzodiazepines & Sleep
  { value: 'Alprazolam', label: 'Alprazolam', category: 'Anxiety/Sleep' },
  { value: 'Lorazepam', label: 'Lorazepam', category: 'Anxiety/Sleep' },
  { value: 'Diazepam', label: 'Diazepam', category: 'Anxiety/Sleep' },
  { value: 'Clonazepam', label: 'Clonazepam', category: 'Anxiety/Sleep' },
  { value: 'Zolpidem', label: 'Zolpidem', category: 'Sleep' },
  { value: 'Zopiclone', label: 'Zopiclone', category: 'Sleep' },
  { value: 'Temazepam', label: 'Temazepam', category: 'Sleep' },
  
  // Anticholinergics
  { value: 'Diphenhydramine', label: 'Diphenhydramine', category: 'Antihistamine/Sleep' },
  { value: 'Oxybutynin', label: 'Oxybutynin', category: 'Bladder' },
  { value: 'Tolterodine', label: 'Tolterodine', category: 'Bladder' },
  
  // Pain
  { value: 'Ibuprofen', label: 'Ibuprofen', category: 'Pain' },
  { value: 'Naproxen', label: 'Naproxen', category: 'Pain' },
  { value: 'Diclofenac', label: 'Diclofenac', category: 'Pain' },
  { value: 'Tramadol', label: 'Tramadol', category: 'Pain' },
  { value: 'Gabapentin', label: 'Gabapentin', category: 'Pain/Nerve' },
  { value: 'Pregabalin', label: 'Pregabalin', category: 'Pain/Nerve' },
  
  // Thyroid
  { value: 'Levothyroxine', label: 'Levothyroxine', category: 'Thyroid' },
  
  // Other
  { value: 'Prednisone', label: 'Prednisone', category: 'Steroid' },
  { value: 'Furosemide', label: 'Furosemide', category: 'Diuretic' },
  { value: 'Hydrochlorothiazide', label: 'Hydrochlorothiazide', category: 'Diuretic' },
];

// Ayurvedic herbs database
export const COMMON_HERBS = [
  { value: 'Ashwagandha', label: 'Ashwagandha', category: 'Adaptogen' },
  { value: 'Turmeric', label: 'Turmeric (Curcumin)', category: 'Anti-inflammatory' },
  { value: 'Brahmi', label: 'Brahmi', category: 'Cognitive' },
  { value: 'Triphala', label: 'Triphala', category: 'Digestive' },
  { value: 'Holy Basil', label: 'Holy Basil (Tulsi)', category: 'Adaptogen' },
  { value: 'Guggul', label: 'Guggul', category: 'Cholesterol' },
  { value: 'Shankhpushpi', label: 'Shankhpushpi', category: 'Cognitive' },
  { value: 'Ginger', label: 'Ginger', category: 'Digestive' },
  { value: 'Boswellia', label: 'Boswellia (Shallaki)', category: 'Anti-inflammatory' },
  { value: 'Neem', label: 'Neem', category: 'Immune' },
  { value: 'Arjuna', label: 'Arjuna', category: 'Heart' },
  { value: 'Shatavari', label: 'Shatavari', category: 'Reproductive' },
  { value: 'Guduchi', label: 'Guduchi', category: 'Immune' },
  { value: 'Haritaki', label: 'Haritaki', category: 'Digestive' },
  { value: 'Amla', label: 'Amla', category: 'Immune' },
  { value: 'Licorice', label: 'Licorice (Yashtimadhu)', category: 'Respiratory' },
  { value: 'Fenugreek', label: 'Fenugreek (Methi)', category: 'Diabetes' },
  { value: 'Moringa', label: 'Moringa', category: 'Nutrition' },
  { value: 'Gokshura', label: 'Gokshura', category: 'Urinary' },
  { value: 'Kalmegh', label: 'Kalmegh', category: 'Immune' },
  { value: 'Chyawanprash', label: 'Chyawanprash', category: 'Rasayana' },
];

// Frequency options
export const FREQUENCY_OPTIONS = [
  { value: 'once daily', label: 'Once daily' },
  { value: 'twice daily', label: 'Twice daily' },
  { value: 'three times daily', label: 'Three times daily' },
  { value: 'four times daily', label: 'Four times daily' },
  { value: 'every morning', label: 'Every morning' },
  { value: 'every evening', label: 'Every evening' },
  { value: 'at bedtime', label: 'At bedtime' },
  { value: 'before meals', label: 'Before meals' },
  { value: 'after meals', label: 'After meals' },
  { value: 'with meals', label: 'With meals' },
  { value: 'every other day', label: 'Every other day' },
  { value: 'as needed', label: 'As needed (PRN)' },
  { value: 'weekly', label: 'Weekly' },
];

// Indication options (grouped)
export const INDICATION_OPTIONS = [
  // Cardiovascular
  { value: 'Hypertension', label: 'Hypertension (High blood pressure)', category: 'Heart' },
  { value: 'Heart failure', label: 'Heart failure', category: 'Heart' },
  { value: 'Atrial fibrillation', label: 'Atrial fibrillation', category: 'Heart' },
  { value: 'Angina', label: 'Angina (Chest pain)', category: 'Heart' },
  { value: 'Primary prevention', label: 'Primary prevention (Cholesterol)', category: 'Heart' },
  { value: 'Secondary prevention', label: 'Secondary prevention (Post-MI/Stroke)', category: 'Heart' },
  
  // Diabetes
  { value: 'Diabetes', label: 'Diabetes (Blood sugar control)', category: 'Metabolic' },
  { value: 'Pre-diabetes', label: 'Pre-diabetes', category: 'Metabolic' },
  
  // Gastrointestinal
  { value: 'GERD', label: 'GERD (Acid reflux)', category: 'Digestive' },
  { value: 'Peptic ulcer', label: 'Peptic ulcer', category: 'Digestive' },
  { value: 'Constipation', label: 'Constipation', category: 'Digestive' },
  
  // Mental Health
  { value: 'Depression', label: 'Depression', category: 'Mental Health' },
  { value: 'Anxiety', label: 'Anxiety', category: 'Mental Health' },
  { value: 'Panic disorder', label: 'Panic disorder', category: 'Mental Health' },
  { value: 'Insomnia', label: 'Insomnia (Sleep)', category: 'Mental Health' },
  
  // Pain
  { value: 'Chronic pain', label: 'Chronic pain', category: 'Pain' },
  { value: 'Arthritis', label: 'Arthritis', category: 'Pain' },
  { value: 'Neuropathic pain', label: 'Neuropathic pain (Nerve pain)', category: 'Pain' },
  
  // Other
  { value: 'Thyroid disorder', label: 'Thyroid disorder', category: 'Endocrine' },
  { value: 'Osteoporosis', label: 'Osteoporosis', category: 'Bone' },
  { value: 'COPD', label: 'COPD', category: 'Respiratory' },
  { value: 'Asthma', label: 'Asthma', category: 'Respiratory' },
  { value: 'Other', label: 'Other', category: 'Other' },
];

// Herbal intended effects
export const HERBAL_EFFECTS = [
  { value: 'sleep', label: 'Sleep / Insomnia' },
  { value: 'stress', label: 'Stress / Anxiety' },
  { value: 'immunity', label: 'Immunity boost' },
  { value: 'inflammation', label: 'Inflammation / Pain' },
  { value: 'digestion', label: 'Digestion / Constipation' },
  { value: 'sugar control', label: 'Blood sugar control' },
  { value: 'cholesterol', label: 'Cholesterol management' },
  { value: 'memory', label: 'Memory / Cognition' },
  { value: 'energy', label: 'Energy / Vitality' },
  { value: 'heart health', label: 'Heart health' },
  { value: 'weight loss', label: 'Weight management' },
  { value: 'skin', label: 'Skin health' },
  { value: 'joint health', label: 'Joint health' },
  { value: 'respiratory', label: 'Respiratory / Cough' },
  { value: 'other', label: 'Other' },
];
