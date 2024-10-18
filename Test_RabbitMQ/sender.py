import pika
import os

def send_dicom_file(file_path):
    #соединение
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    #проверка очереди или создание, отправка
    channel.queue_declare(queue='dicom_queue')
    channel.basic_publish(exchange='', routing_key='dicom_queue', body=file_path)
    print(f" Отправка пути {file_path}")

    connection.close()

dicom_file_path = "C:/Users/bayut/Desktop/test_data/BVL250941/00000001"
send_dicom_file(dicom_file_path)


dicom_file_path = "C:/Users/bayut/Desktop/test_data/BVL250941/00000002"
send_dicom_file(dicom_file_path)

dicom_file_path = "C:/Users/bayut/Desktop/test_data/BVL250941/00000003"
send_dicom_file(dicom_file_path)

dicom_file_path = "C:/Users/bayut/Desktop/test_data/BVL250941/00000013"
send_dicom_file(dicom_file_path)