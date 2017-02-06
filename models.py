from django.db import models
from django.core.validators import RegexValidator

grade_choices = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
)


class Offer(models.Model):
    place = models.CharField(max_length=200)
    target_date = models.DateTimeField(unique=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Numer telefonu musi być podany w formacie: '+999999999'")
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=200)
    email = models.EmailField(blank=True)

    full_cleaning = models.BooleanField(default=False)
    car_cleaning = models.BooleanField(default=False)
    window_cleaning = models.BooleanField(default=False)
    price = models.FloatField(blank=True)
    living_room = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)
    bathroom = models.BooleanField(default=False)
    bedroom = models.BooleanField(default=False)

    author = models.ForeignKey('auth.User', blank=True, null=True)
    chosen_worker = models.ForeignKey('SignedWorker', null=True, blank=True)
    worker_accepted = models.BooleanField(default=False)

    def __str__(self):
        return '%s and %s' % (self.author, self.place)


class SignedWorker(models.Model):
    signed_offer = models.ForeignKey('Offer')
    worker = models.ForeignKey('auth.User')

    def __str__(self):
        return str(self.worker)


class Rank(models.Model):
    grade = models.CharField(choices=grade_choices, max_length=255)
    opinion = models.TextField(max_length=255)
    user = models.ForeignKey('auth.User')

    def __str__(self):
        return '%s and %s' % (self.user, self.grade)
