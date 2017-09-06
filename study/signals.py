from django.db.models.signals import post_save
from django.dispatch import receiver

from study.models import DeviceSettings, Study


@receiver(post_save, sender=Study)
def populate_study_device_settings(sender, **kwargs):
    """
    Ensure that every newly created Study object has a DeviceSettings object. This essentially
    makes the OneToOneField have null=False in both directions.
    """

    my_study = kwargs['instance']
    if kwargs['created'] and not hasattr(my_study, 'device_settings'):
        # If my_study has just been created and doesn't have a DeviceSettings
        # attached to it, create one with the default parameters.
        DeviceSettings.objects.create(study=my_study)
