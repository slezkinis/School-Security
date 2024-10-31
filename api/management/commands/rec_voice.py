from django.core.management.base import BaseCommand
from api.models import Employee
import pveagle
from school_security.settings import PVEAGLE_KEY
from pvrecorder import PvRecorder



DEFAULT_DEVICE_INDEX = 0

class Command(BaseCommand):
    help = 'Программа записывает голос и присоединяет егот к профилю работника'

    def add_arguments(self, parser):
        parser.add_argument(
            'id',
            help='ID пользователя',
            type=int,
        )

    def handle(self, *args, **options):
        try:
            employee = Employee.objects.get(id=options["id"])
        except Employee.DoesNotExist:
            print("[ERROR] Пользователь с таким ID не найден!")
            return
        eagle_profiler = pveagle.create_profiler(access_key=PVEAGLE_KEY)
        
        enroll_recorder = PvRecorder(
            device_index=DEFAULT_DEVICE_INDEX,
            frame_length=eagle_profiler.min_enroll_samples)
        print("Говорите до тех пор, пока не появится запись. Старайтесь говорить своим голосом")
        enroll_recorder.start()

        enroll_percentage = 0.0
        while enroll_percentage < 100.0:
            audio_frame = enroll_recorder.read()
            enroll_percentage, feedback = eagle_profiler.enroll(audio_frame)

        enroll_recorder.stop()
        speaker_profile1 = eagle_profiler.export()
        employee.voice_profile = speaker_profile1.to_bytes()
        employee.save()
        print("Голос записан!")