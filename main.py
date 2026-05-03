import cv2
import numpy as np
import tensorflow as tf
import pyttsx3
import time
import os

# --- SETUP PATH FILE OTOMATIS ---
folder_ini = os.path.dirname(os.path.abspath(__file__))
path_model = os.path.join(folder_ini, "model.tflite")
path_label = os.path.join(folder_ini, "labels.txt")

# --- 1. SETUP SUARA (TTS) ---
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
except:
    print("Warning: Speaker bermasalah, tapi program jalan terus.")

def ngomong(teks):
    print(f"🗣️ Mengucapkan: {teks}")
    try:
        engine.say(teks)
        engine.runAndWait()
    except:
        pass

# --- 2. SETUP KAMERA & TFLITE ---
print(f"Sedang mencari model di: {path_model}")

try:
    # LOAD MODEL
    interpreter = tf.lite.Interpreter(model_path=path_model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    with open(path_label, "r") as f:
        class_names = [line.strip() for line in f.readlines()]

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Tambah CAP_DSHOW biar aman di Windows
    print("\n✅ BERHASIL! Kamera siap. Tekan 'ESC' buat keluar.")

    # --- VARIABEL LOGIKA SUARA ---
    last_speak_time = 0
    jeda_suara = 3
    last_class_name = ""  # <--- Ini variabel ingatan jangka pendek

    while True:
        ret, image = camera.read()
        if not ret: break

        # --- PROSES GAMBAR ---
        img_resized = cv2.resize(image, (224, 224))
        input_data = np.asarray(img_resized, dtype=np.float32)
        input_data = (input_data / 127.5) - 1.0
        input_data = np.expand_dims(input_data, axis=0)

        # --- PREDIKSI ---
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        index = np.argmax(output_data)
        confidence_score = output_data[0][index]
        
        raw_label = class_names[index]
        class_name = raw_label[2:] if raw_label[0].isdigit() else raw_label

        # Tampilkan teks
        text_display = f"{class_name}: {int(confidence_score * 100)}%"
        color = (0, 255, 0) if confidence_score > 0.5 else (0, 0, 255)
        cv2.putText(image, text_display, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # --- LOGIKA SUARA CERDAS (FINAL) ---
        if confidence_score > 0.5: # Ambang batas 50%
            current_time = time.time()
            
            # Cek: Apakah bendanya BARU? ATAU Apakah jeda waktu sudah lewat?
            if (class_name != last_class_name) or (current_time - last_speak_time > jeda_suara):
                
                # Filter Background
                if "Background" not in raw_label and "Class" not in raw_label:
                    kalimat = f"Ini adalah sampah {class_name}"
                    ngomong(kalimat)
                    
                    last_speak_time = current_time
                    last_class_name = class_name # Ingat benda ini!

        else:
            # Kalau gak yakin, reset ingatan biar nanti kalau yakin lagi langsung ngomong
            last_class_name = ""

        cv2.imshow("Project IoT Sampah", image)

        if cv2.waitKey(1) == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

except Exception as e:
    print(f"\n❌ ERROR: {e}")