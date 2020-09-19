from django.db import models
from user.models import userRegister

class coachRegister(models.Model):
    name=models.CharField(max_length=256, null=True, blank=True)
    email=models.CharField(max_length=256, null=True, blank=True)
    mobile=models.CharField(max_length=256, null=True, blank=True)
    approved=models.BooleanField(default=False)
    updated_bio=models.BooleanField(default=False)
    password=models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name

class CoachBio(models.Model):
    bio = models.TextField()
    url = models.CharField(max_length=256, null=True, blank=True)
    banner  = models.CharField(max_length=256, null=True, blank=True)
    logo    = models.CharField(max_length=256, null=True, blank=True)
    coach   = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='coach_bio',null=True,blank=True)
    

class ToggleSections(models.Model):
    bio  = models.BooleanField(default=True)
    workout  = models.BooleanField(default=True)
    playlist  = models.BooleanField(default=True)
    statistics  = models.BooleanField(default=True)
    coach   = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='toggle_sections',null=True,blank=True)


class Playlist(models.Model):
    title  = models.CharField(max_length=256, null=True, blank=True)
    description    = models.TextField()
    thumbnail = models.CharField(max_length=256, null=True, blank=True)
    tags  = models.CharField(max_length=256, null=True, blank=True)
    level  = models.CharField(max_length=256, null=True, blank=True)
    duration    = models.CharField(max_length=256, null=True, blank=True)
    coach   = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='coach_playlist',null=True,blank=True)
    
    def __str__(self):
        return self.title

class Associated(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='associated_users',null=True,blank=True)
    user =  models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='associated_users',null=True,blank=True)
    active  = models.BooleanField(default=False)


class Video(models.Model):
    title  = models.CharField(max_length=256, null=True, blank=True)
    description    = models.TextField()
    video = models.CharField(max_length=256, null=True, blank=True)
    thumbnail = models.CharField(max_length=256, null=True, blank=True)
    tags  = models.CharField(max_length=256, null=True, blank=True)
    equipments    = models.CharField(max_length=256, null=True, blank=True)
    calories  = models.CharField(max_length=256, null=True, blank=True)
    duration    = models.CharField(max_length=256, null=True, blank=True)
    accesstype = models.IntegerField(default=1)
    playlist   = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='coach_videos',null=True,blank=True)
    coach   = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='coach_videos',null=True,blank=True)
    
    def __str__(self):
        return self.title

class VideoAccessForPrivateVideos(models.Model):
    video =  models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_access_for_private_videos',null=True,blank=True)
    user =  models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='video_access_for_private_videos',null=True,blank=True)


class Otp(models.Model):
    email=models.CharField(max_length=256, null=True, blank=True)
    otp=models.IntegerField()

    def __str__(self):
        return self.otp

class PlayListVideos(models.Model):
    coach      = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='playlist_videos',null=True,blank=True)
    video      = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='playlists_videos',null=True,blank=True)
    playlist   = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlists_videos',null=True,blank=True)
    # serial     = models.IntegerField(null=True, blank=True)


class Review(models.Model):
    rating      = models.IntegerField(null=True, blank=True)
    added_on    = models.DateTimeField(auto_now_add=True)
    coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='review',null=True,blank=True)
    user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='review',null=True,blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='review',null=True,blank=True)


class Testimonial(models.Model):
    testimonial = models.TextField()
    added_on    = models.DateTimeField(auto_now_add=True)
    coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='testimonials',null=True,blank=True)
    user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='testimonials',null=True,blank=True)


class Comments(models.Model):
    comment     = models.CharField(max_length=256,null=True, blank=True)
    added_on    = models.DateTimeField(auto_now_add=True)
    coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)
    user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)

    def __str__(self):
        return self.comment

class NoOfPlayedTimes(models.Model):
    no_of_played_times              = models.IntegerField(null=True, blank=True)
    coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='noofplayedtimes',null=True,blank=True)
    user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='noofplayedtimes',null=True,blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='noofplayedtimes',null=True,blank=True)

class NoOfUsersWhoHaveSeen(models.Model):
    no_of_users_who_have_seen =models.IntegerField(null=True, blank=True)
    coach_id       = models.IntegerField(null=True, blank=True)
    user_id        = models.IntegerField(null=True, blank=True)
    video_id = models.IntegerField(null=True, blank=True)

class AvgViewTime(models.Model):
    avg_view_time = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    coach_id       = models.IntegerField(null=True, blank=True)
    user_id        = models.IntegerField(null=True, blank=True)
    video_id = models.IntegerField(null=True, blank=True)

class Likes(models.Model):
    like        = models.IntegerField(null=True, blank=True)
    added_on    = models.DateTimeField(auto_now_add=True)
    coach_id    = models.IntegerField(null=True, blank=True)
    user_id     = models.IntegerField(null=True, blank=True)
    video_id    = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.like

# class Statistics(models.Model):
#     no_of_played_times              = models.CharField(max_length=256,null=True, blank=True)
#     # no_of_users_allowed             = models.CharField(max_length=256,null=True, blank=True)
#     no_of_users_who_have_seen       = models.CharField(max_length=256,null=True, blank=True)
#     avg_view_time                   = models.CharField(max_length=256,null=True, blank=True)
#     # no_of_playlists_the_video_is_in = models.CharField(max_length=256,null=True, blank=True)
#     coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='statistics',null=True,blank=True)
#     user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='statistics',null=True,blank=True)
#     video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='statistics',null=True,blank=True)




# class VideosModel(models.Model):
#     url         = models.CharField(max_length=256, null=True, blank=True)
#     upadated_on = models.DateTimeField(auto_now_add=True)
#     title       = models.CharField(max_length=256, null=True, blank=True)
#     duration    = models.CharField(max_length=256, null=True, blank=True, default=0)
#     level       = models.IntegerField(null=True, blank=True)
#     tags        = models.CharField(max_length=256, null=True, blank=True)
#     views       = models.IntegerField(default=0)
#     coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='video_models',null=True,blank=True)

#     def __str__(self):
#         return self.url



# class PlayLists(models.Model):
#     name       = models.CharField(max_length=256, null=True, blank=True)
#     created_on = models.DateTimeField(auto_now_add=True)
#     thumbnail  = models.FileField(null=True, blank=True)
#     thumbnail_url = models.CharField(max_length=256, null=True, blank=True)
#     difficulty = models.IntegerField(null=True, blank=True)
#     coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='playlists',null=True,blank=True)

#     def __str__(self):
#         return self.name



# # daily pass
# # anyone can see
