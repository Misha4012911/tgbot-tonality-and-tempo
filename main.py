import telebot
import os
from pydub import AudioSegment
import math
import aubio

# Введите здесь токен своего Telegram-бота
bot = telebot.TeleBot("6117737701:AAFAc78SiWTGjVUhojJauB5rRWnyTxrA5XM")

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    # Получаем информацию об аудиофайле
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем файл на диск
    file_name = message.audio.file_name
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Анализируем аудиофайл
    tempo, pitch = analyze_audio(file_path)

    # Отправляем результаты анализа в чат с пользователем
    bot.send_message(message.chat.id, f"Tempo: {tempo} BPM\nPitch: {pitch} Hz")

    # Удаляем файл с диска, чтобы не засорять память сервера
    os.remove(file_path)

def analyze_audio(file_path):
    # Load audio file using pydub
    sound = AudioSegment.from_file(file_path)
    tempo = sound.duration_seconds / (len(sound) / 1000) * 60
    
    # Calculate pitch using aubio
    pitch_detection = aubio.pitch("yinfft", 2048, 2048//2, 44100)
    pitch_detection.set_unit("Hz")
    pitch_detection.set_silence(-40)
    
    audio_file = aubio.source(file_path)
    total_frames = 0
    pitch_sum = 0.0
    while True:
        samples, read = audio_file()
        pitch = pitch_detection(samples)[0]
        if pitch != 0:
            pitch_sum += pitch
            total_frames += read
        if read < 2048:
            break
    
    # Calculate the average pitch
    if total_frames > 0:
        avg_pitch = pitch_sum/total_frames
    else:
        avg_pitch = 0

    # Return tempo and pitch
    return math.floor(tempo), int(round(avg_pitch))

bot.polling()