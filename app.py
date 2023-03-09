from flask import Flask, request, render_template
import os
import subprocess
import datetime

from time import sleep
import openai
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():


    def divide_by_chunks(file_path):
        # set the path to the mp3 file
        filename = file_path.split('\\')[-1].split('/')[-1]
        filename = "".join(filename.split('.')[:-1])
        audio_path = file_path

        # set the length of each chunk in milliseconds (10 minutes = 600000 milliseconds)
        chunk_length_ms = 1400000

        # create an AudioSegment object from the mp3 file
        audio = AudioSegment.from_file(audio_path)

        # get the length of the audio in milliseconds
        audio_length_ms = len(audio)

        # determine the number of chunks needed
        num_chunks = int(audio_length_ms / chunk_length_ms) + 1

        # create a directory to store the chunks
        output_dir = 'chunks'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_chunks_list = []
        # split the audio into chunks and save each chunk as a separate mp3 file
        for i in range(num_chunks):
            start = i * chunk_length_ms
            end = min((i + 1) * chunk_length_ms, audio_length_ms)
            chunk = audio[start:end]
            chunk_file = f"{output_dir}/{filename}_chunk_{i+1}.mp3"
            chunk.export(chunk_file, format="mp3")
            file_chunks_list.append(chunk_file)

        return file_chunks_list

    def is_video_file(file_path):
        try:
            video = VideoFileClip(file_path)
            return True
        except Exception as e:
            return False

    def video_to_audio(video_file, audio_file):
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(audio_file)


    ## Summarize
    def summarize_text(file_path,apikey):

        

        file_path = file_path.replace('\\','/').replace('uploads','audio_transcription')+".txt"

        # Define the text to be summarized
        text = open(f"{file_path}", "r",encoding="utf-8").read()

        limit = 12000
        loops = (len(text)//limit)+1
        message_list = []
        for n in range(loops):
            n +=1
            if (n!=loops) or (n==1):
                t = text[(n-1)*limit:n*limit]
            else:
                t = text[(n-1)*limit:]

            # Define the prompt for summarization
            #prompt = f"El siguiente texto es una conversacion, porfavor resumelo y enumera los puntos mas importantes, es importante que no falte ningun tema mencionado:\n\n{t}"
            prompt = f"""
            Haz todo lo posible por desarrollar el siguiente texto. Es importante ENUMERAR y DESARROLLAR 
            a plenitud cada uno de los temas sin que falte ningun punto importante de lo tratado. Repito es IMPORTANTE 
            que no falte ninguno de los temas tratados
            Texto:
            {t}
            """


            # Generate a summary
            model_engine = "gpt-3.5-turbo"
            completions = openai.ChatCompletion.create(model=model_engine, messages=[
                    {"role": "system", "content": "Tu eres un asistente muy servicial."},
                    {"role": "user", "content":prompt}])
            message =completions.choices[0].message.content
            message_list.append(message)


        if len(message_list)==1:
            message_final = "".join(message_list)

        else:
            t2 = "\n\n=== Minuta:\n".join(message_list)
            # Define the prompt for summarization
            #prompt = f"Porfavor combina estos {len(message_list)} resumenes en uno solo y los puntos enumerados en una sola lista, es importante que no falte ningun tema mencionado:\n\n{t2}"

            prompt = f"""
            Haz todo lo posible por combinar estos textos y convertirlos en una minuta. 
            Es IMPORTANTE que no falte ninguno de los temas tratados.

            Aqui te dejo un ejemplo del que te puedes guiar

            ========= Ejemplo:
            Minuta de Asamblea [a completar]

            Fecha: [a completar]

            Hora de inicio: [a completar]

            Lugar: Virtual a través de Zoom y YouTube

            Asistentes: Todos los miembros del consejo, propietarios de condominios

            Punto 1. Bienvenida y agradecimiento

            Se da la bienvenida a todos los propietarios de condominios y se agradece por asistir a la asamblea vía Zoom debido a la pandemia de COVID-19. Los miembros del consejo presentes son el tesorero, el secretario Armando de León, Christopher, George y la presidenta Norma Miranda. También se agradece al señor Jeff por su ayuda en la traducción al inglés.

            Punto 2. Logros del año pasado (2021)

            - Remodelación de pasillos en piedra alha roja detrás de la oficina de la Torre D y en la salida de la puerta del cuarto de máquinas.
            - Remodelación de la escalera de la entrada de la Torre B.
            - Sellado de la piedra roja en todos los pasillos de aires comunes.
            - Instalación del techo de la entrada del condominio para proteger el estacionamiento.
            - Construcción de un nuevo baño para las empleadas.
            - Reparación del tejado y cambio de algunas vigas en la oficina de la administración.
            - Reparación de varias fugas de agua y gas en diferentes áreas del condominio.

            Punto 3. Programa de impermeabilización de techos y pintura

            - Instalación del manto prefabricado para la impermeabilización en 6 departamentos.
            - Pintura de todo el edificio B y áreas comunes del condominio.
            - Finalización del programa de impermeabilización de techos este año (2022).


            Punto 5. Agradecimiento

            Se agradece a todos los propietarios por su compromiso en mantener sus mantenimientos al día.

            Punto 6. Verificación del quórum legal para la asamblea

            Se verificó el quórum legal para la asamblea y se determinó que el 53% de los propietarios de condominios votaron.

            Punto 7. Discusión y aprobación del presupuesto de ingresos y egresos para este año

            El 53% de los propietarios de condominios aprobaron la cuota de mantenimiento de este año.

            Punto 8. Discusión y aprobación de continuar el mismo consejo de administración

            La gráfica mostró que la mayoría de los propietarios votaron para continuar con el mismo consejo de administración para el próximo año.

            Hora de finalización: [a completar]


            ========= Textos:
            {t2}
            """

            # Generate a summary
            model_engine = "gpt-3.5-turbo"
            completions = openai.ChatCompletion.create(model=model_engine, messages=[
                    {"role": "system", "content": "Tu eres un asistente muy servicial."},
                    {"role": "user", "content":prompt}])
            message_final =completions.choices[0].message.content

        filename_res = file_path.split('.')[0].split('\\')[-1].split('/')[-1]
        with open(f"results/{filename_res}.txt", 'w') as f:
            f.write(message_final)

        print(message_final)

            
        return message_final


        
    # Apply API key
    apikey = open("../api-key.txt", "r").read().replace("\n","")
    
    openai.api_key = apikey

    file = request.files['file']
    uploads_dir = os.path.join(app.root_path, "uploads")
    filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + file.filename
    file_path = os.path.join(uploads_dir, filename)
    file.save(file_path)

    if filename.endswith('ogg'):
        ogg_file = AudioSegment.from_file(file_path, format="ogg")
        new_file_path = "".join(file_path.split(".")[:-1])+".mp3"
        ogg_file.export(new_file_path, format="mp3")
        file_path = new_file_path
        filename = file_path.split('\\')[-1].split('/')[-1]
        print(filename)

    # if is_video_file(file_path):
    #     new_file_path = "".join(file_path.split(".")[:-1])+".mp3"
    #     video_to_audio(file_path, new_file_path)
    #     file_path = new_file_path
    #     filename = file_path.split('\\')[-1].split('/')[-1]

    # VERSION WHISPER GPU LOCAL
    #command = f"whisper {file_path} --task transcribe --model medium --verbose False --device cuda --output_dir audio_transcription"
    #subprocess.run(command, shell=True)


    # VERSION WHISPER API
    file_chunks_list = divide_by_chunks(file_path) # Esto es necesario porque la version de api tiene un limite
    transcript_all = []
    for f in file_chunks_list:

        audio_file= open(f, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        transcript = transcript['text']
        transcript_all.append(transcript)

    transcript = "".join(transcript_all)

    with open("audio_transcription/"+filename+".txt", 'w',encoding="utf-8") as f:
        f.write(transcript)

    try:
        message_final = summarize_text(file_path,apikey)
    except Exception as e:
        print('Se intentara de nuevo, hubo un problema de tipo ', e)
        sleep(3)
        try:
            message_final = summarize_text(file_path,apikey)
        except Exception as e:
            print('Otra vez, hubo un problema de tipo ', e)


    message_final = message_final.replace("\n", "<br>")
    return render_template('received.html', message_final=message_final)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = datetime.timedelta(minutes=30)

    app.run(debug=True,host='0.0.0.0',port=5000)
    #app.run()
