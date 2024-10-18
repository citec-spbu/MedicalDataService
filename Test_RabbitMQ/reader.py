import pika
import pydicom
import matplotlib.pyplot as plt


#чтение файла
def process_dicom(file_path):
    try:
        ds = pydicom.dcmread(file_path)
        print("DICOM:")
        print(ds)

        if 'PixelData' in ds:
            plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
            plt.title(f"UID: {ds.SOPInstanceUID}")
            plt.axis('off')
            plt.show()
        else:
            print("нет изображения")
    except Exception as e:
        print(f"Err: {e}")


def callback(ch, method, properties, body):
    file_path = body.decode()
    print(f" [!!!] Получен путь: {file_path}")
    process_dicom(file_path)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='dicom_queue')

#обратный вызов
channel.basic_consume(queue='dicom_queue', on_message_callback=callback, auto_ack=True)

print('Ожидание')
channel.start_consuming()
