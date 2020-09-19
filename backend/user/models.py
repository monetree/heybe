from django.db import models

class userRegister(models.Model):
    name=models.CharField(max_length=256, null=True, blank=True)
    email=models.CharField(max_length=256, null=True, blank=True)
    password=models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name


class Otp(models.Model):
    email=models.CharField(max_length=256, null=True, blank=True)
    otp=models.IntegerField()

    def __str__(self):
        return self.otp



# class WatchLater(models.Model):
#     user  = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='watch_laters',null=True,blank=True)
#     video = models.ForeignKey(VideosModel, on_delete=models.CASCADE, related_name='watch_laters',null=True,blank=True)

#     def __str__(self):
#         return self.video


# class Comments(models.Model):
#     comment     = models.CharField(max_length=256,null=True, blank=True)
#     added_on    = models.DateTimeField(auto_now_add=True)
#     coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)
#     user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)
#     video_model = models.ForeignKey(VideosModel, on_delete=models.CASCADE, related_name='comments',null=True,blank=True)

#     def __str__(self):
#         return self.comment

# class Likes(models.Model):
#     like        = models.IntegerField(null=True, blank=True)
#     added_on    = models.DateTimeField(auto_now_add=True)
#     coach       = models.ForeignKey(coachRegister, on_delete=models.CASCADE, related_name='likes',null=True,blank=True)
#     user        = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='likes',null=True,blank=True)
#     video_model = models.ForeignKey(VideosModel, on_delete=models.CASCADE, related_name='likes',null=True,blank=True)

#     def __str__(self):
#         return self.like




# class SaveToPlaylist(models.Model):
#     user     = models.ForeignKey(userRegister, on_delete=models.CASCADE, related_name='save_to_playlist',null=True,blank=True)
#     playlist = models.ForeignKey(PlayLists, on_delete=models.CASCADE, related_name='save_to_playlist',null=True,blank=True)
