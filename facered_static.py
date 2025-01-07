import cv2
import face_recognition
import os
import time

# Caminho para a pasta "people"
current_directory = os.path.dirname(os.path.abspath(__file__))
people_directory = os.path.join(current_directory, "people")

# Arrays para armazenar encodings e nomes
known_face_encodings = []
known_face_names = []
known_face_images = []

# Percorre os arquivos na pasta "people"
for filename in os.listdir(people_directory):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        file_path = os.path.join(people_directory, filename)

        # Carrega a imagem
        image = face_recognition.load_image_file(file_path)

        # Extrai os encodings da face (considera apenas a primeira face encontrada)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])
            known_face_images.append(cv2.imread(file_path))

# Inicializa a webcam
video_capture = cv2.VideoCapture(0)

# Dimensões do quadrado no meio da tela
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


#******************************
#Mudar para 500 no MAC
square_size = 250

x_start = frame_width // 2 - square_size // 2
y_start = frame_height // 2 - square_size // 2
x_end = x_start + square_size
y_end = y_start + square_size

# Tempo de espera entre verificações
wait_time = 5
last_check_time = time.time() - wait_time

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Desenha o quadrado no meio da tela
    cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

    # Verifica se o tempo de espera passou
    if time.time() - last_check_time >= wait_time:
        # Recorta a área do quadrado
        roi = frame[y_start:y_end, x_start:x_end]
        rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        # Procura faces na região do quadrado
        face_encodings = face_recognition.face_encodings(rgb_roi)

        if face_encodings:
            # Usa apenas a primeira face detectada
            face_encoding = face_encodings[0]

            # Compara com as faces conhecidas
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            if any(matches):
                # Identifica a face com menor distância
                best_match_index = matches.index(True)

                # Mostra a foto da pessoa conhecida
                person_image = known_face_images[best_match_index]
                person_name = known_face_names[best_match_index]

                person_image = cv2.resize(person_image, (square_size, square_size))

                # Coloca a imagem da pessoa reconhecida no frame
                frame[0:square_size, 0:square_size] = person_image
                frame[0:square_size, square_size:square_size*2] = roi

                # Adiciona o nome da pessoa reconhecida abaixo das imagens
                cv2.putText(frame, person_name, (10, square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                print(f"Pessoa reconhecida: {person_name}")

                # Exibe o frame da webcam com as imagens por 4 segundos
                cv2.imshow("Webcam", frame)
                cv2.waitKey(4000)

            else:
                print("Pessoa não reconhecida")
        else:
            print("Nenhuma face detectada no quadrado")

        # Atualiza o último tempo de verificação
        last_check_time = time.time()

    # Exibe o frame da webcam
    cv2.imshow("Webcam", frame)

    # Verifica se a tecla 'q' foi pressionada para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a webcam e fecha as janelas
video_capture.release()
cv2.destroyAllWindows()
