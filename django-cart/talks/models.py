from django.contrib.sites.models import Site
from django.db import models
from django.conf import settings

class Talk(models.Model):
	title = models.CharField(maxlength=400)
	teacher = models.ForeignKey(Teacher)
	description = models.TextField(maxlength=2048, blank=True)
	venue = models.ForeignKey(Venue, blank=True, null=True, help_text='Leave blank for retreat talks')
	retreat = models.ForeignKey(Retreat, blank=True, null=True, help_text='Leave blank if not a retreat talk')
	uploadedAudio = models.FileField(upload_to=UPLOAD_DIR, blank=True)
	rec_date = models.DateField('Date Recorded', help_text='YYYY-MM-DD')
	talk_code = models.CharField(maxlength=30, blank=True)
	spoken_language = models.CharField(maxlength=30, blank=True, help_text='Leave blank for English')
	source_recording_format = \
		models.CharField('Source Recording Format', maxlength=10, choices=source_formats, blank=True)
	source_recording_quality = \
		models.CharField('Source Recording Quality', maxlength=10, choices=(('High','High'),('Medium','Medium'),('Low','Low')), blank=True)
	isPublishable = models.BooleanField(default=False, help_text='Uncheck for talks available only to retreatants')

	destination = \
		models.CharField(maxlength=10, choices=talk_destinations, \
		help_text='Indicate whether material is going directly to the website or to Dharma Seed for processing')

	def audioUrl(self):
		url = '/media/%s' % re.sub('.*media/','', self.uploadedAudio)
		return url

	def streamUrl(self):
		url = re.sub('.*media/','/', self.uploadedAudio)
		url = re.sub('mp3$','m3u', url)
		return url

	def orderUrl(self):
		url = '/shop/cart/add/%s/testcookie' % self.talk_code
		return url

	def __str__(self):
		return self.title + ': ' + self.teacher.name

	def renameUpload(self, src):
		dir, fn = src
		file, ext = os.path.splitext(fn)
		return os.path.join(dir, self.talk_code + ext)
		
	def save(self):
		self.talk_code = self.teacher.teacher_code + self.rec_date.__str__().replace('-','')
		super(Talk, self).save() # Call the "real" save() method.

	
	class Admin:
		ordering = ['title']
		list_filter = ('destination',)
		fields = (
			(None,
			 {'fields': ('title','teacher','description',
						 'venue','retreat','uploadedAudio','spoken_language',
						 'isPublishable','destination',
						 'rec_date','source_recording_format','source_recording_quality')}),
			)
	

