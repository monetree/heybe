from django.shortcuts import render
from .models import userRegister, Otp
from coach.models import (
        Associated, 
        Playlist, 
        PlayListVideos, 
        coachRegister
    )
from django.http import JsonResponse
from .utils import send_mail
import random
import json
# from coach.models import VideosModel,PlayLists
from django.db.models import Count
from django.contrib.auth.hashers import make_password, check_password


class UserAuth:
    def user_register(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            name= ds['name']
            email=ds['email']
            password=ds['password']

            count_email = userRegister.objects.filter(email=email).count()

            if count_email > 0:
                return JsonResponse({"code":422,"msg":"duplicate email"})

            obj = userRegister.objects.create(name=name,email=email, password=make_password(password, salt=None, hasher='default'))
            if obj:
                id = list(userRegister.objects.filter(email=email).values('id'))[0]['id']
                return JsonResponse({'code':200, 'message':'success', 'id':id, 'email': email, 'name':name})
            else:
                return JsonResponse({'code':500, 'message':'Internal server error'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})


    def user_login(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            password=ds['password']
            count = userRegister.objects.filter(email=email).count()
            if count > 0:
                hashed_password = list(userRegister.objects.filter(email=email).values('password'))[0]['password']
                match = check_password(password, hashed_password)
                if not match:
                    return JsonResponse({ 'code':400, 'message':'Invalid credentials'})
                id = list(userRegister.objects.filter(email=email).values('id'))[0]['id']
                name = list(userRegister.objects.filter(email=email).values('name'))[0]['name']
                return JsonResponse({'code':200, 'message':'success', 'id':id, 'email': email, 'name':name})
            else:
                return JsonResponse({'code':400, 'message':'invalid credentails'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})


    def user_forgot_password(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            count = userRegister.objects.filter(email=email).count()
            if count > 0:
                otp = random.randint(999,9999)
                mail = send_mail(email, otp)
                if send_mail:
                    obj = Otp.objects.create(otp=otp, email=email)
                    if obj:
                        return JsonResponse({'code':200, 'message':'verify otp', 'email':email})
                    else:
                        return JsonResponse({'code':500, 'message':'Internal server error'})
                else:
                    return JsonResponse({'code':500, 'message':'Internal server error'})
            else:
                return JsonResponse({'code':400, 'message':'email not exist'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})

    def user_verify_otp(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            otp = ds['otp']
            print(otp)
            # email = ds['email']
            count= Otp.objects.filter(otp=int(otp)).count()
            if count > 0:
                return JsonResponse({'code':200, 'message':'verify otp'})
            else:
                return JsonResponse({'code':400, 'message':'otp is wrong'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})

    def user_reset_password(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            password=ds['password']
            obj= userRegister.objects.filter(email=email).update(password=make_password(password, salt=None, hasher='default'))
            if obj:
                return JsonResponse({'code':200, 'message':'success'})
            else:
                return JsonResponse({'code':500, 'message':'Internal server error'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})

def users(request):
    users = list(userRegister.objects.values('name', 'id'))
    return JsonResponse(users, safe=False)

def associated_playlists(request):
    user_id = request.GET.get("user_id")
    playlist_ids = list(Associated.objects.filter(user_id=int(user_id)).values('playlist_id','active','id'))
    for i in playlist_ids:
        playlists = list(Playlist.objects.filter(id=i["playlist_id"]).values())[0]
        videos = PlayListVideos.objects.filter(playlist_id=playlists["id"]).count()
        coach_name = list(coachRegister.objects.filter(id=playlists["coach_id"]).values('name'))[0]
        i["playlist_id"] = playlists["id"]
        i["title"]= playlists["title"]
        i["description"]= playlists["description"]
        i["thumbnail"]= playlists["thumbnail"]
        i["tags"]= playlists["tags"]
        i["level"]= playlists["level"]
        i["duration"]= playlists["duration"]
        i["coach_id"]= playlists["coach_id"]
        i["workouts"] = videos
        i["coach_name"] = coach_name["name"]
    return JsonResponse(playlist_ids, safe=False)

# def comments(request):
#     if request.method == 'POST':
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         video_id = ds['video_id']
#         coach = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         video = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         comment=ds['comment']
#         user=ds["user"]
#         if len(str(user)) < 1:
#             user = None
#         obj= Comments.objects.create(comment=comment,coach_id=int(coach),user_id=int(user),video_model_id=int(video))
#         if obj:
#             return JsonResponse({'code':200, 'message':'success'})
#         else:
#             return JsonResponse({'code':500, 'message':'Internal server error'})
#     elif request.method == "GET":
#         video_id = request.GET.get('video_id')
#         if video_id:
#             id = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#             res = list(Comments.objects.filter(video_model_id=id).values('user__name','comment','added_on','coach','user','video_model'))
#             return JsonResponse(res, safe=False)
#         res = list(Comments.objects.values('user__name','comment','added_on','coach','user','video_model'))
#         return JsonResponse(res, safe=False)
#     else:
#         return JsonResponse({'code':500, 'message':'Bad Request'})

# def likes(request):
#     if request.method == 'POST':
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         video_id = ds['video_id']
#         coach = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         video = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         like=ds['like']
#         user=ds["user"]
#         obj= Likes.objects.create(like=int(like),coach_id=int(coach),user_id=int(user),video_model_id=int(video))
#         if obj:
#             return JsonResponse({'code':200, 'message':'success'})
#         else:
#             return JsonResponse({'code':500, 'message':'Internal server error'})
#     else:
#         return JsonResponse({'code':500, 'message':'Bad Request'})

# def get_likes(request):
#     video_id = request.GET.get('video_id')
#     if video_id:

#         id = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         res = list(Likes.objects.filter(video_model_id=id, like=1).values())
#         return JsonResponse(res, safe=False)
#     res = list(Likes.objects.values())
#     return JsonResponse(res, safe=False)

# def get_dislikes(request):
#     video_id = request.GET.get('video_id')
#     if video_id:
#         id = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         res = list(Likes.objects.filter(video_model_id=id, like=2).values())
#         return JsonResponse(res, safe=False)
#     res = list(Likes.objects.values())
#     return JsonResponse(res, safe=False)

# from django.db.models import Sum
# def get_review(request):
#     video_id = request.GET.get('video_id')
#     if video_id:
#         id = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         sum = Review.objects.filter(video_model_id=id).all().aggregate(Sum('rating'))['rating__sum']
#         count = Review.objects.filter(video_model_id=id).all().count() * 5
#         review = (sum/count) * 5
#         return JsonResponse({"review":review})
#     else:
#         return JsonResponse({"code":400,"msg":"video_id required"})



# def review(request):
#     if request.method == 'POST':
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         video_id = ds['video_id']
#         print(video_id)
#         coach = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         video = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#         rating=ds['rating']
#         user=ds["user"]
#         obj= Review.objects.create(rating=int(rating),coach_id=int(coach),user_id=int(user),video_model_id=int(video))
#         if obj:
#             return JsonResponse({'code':200, 'message':'success'})
#         else:
#             return JsonResponse({'code':500, 'message':'Internal server error'})
#     elif request.method == "GET":
#         res = list(Review.objects.values())
#         return JsonResponse(res, safe=False)
#     else:
#         return JsonResponse({'code':500, 'message':'Bad Request'})

# def check_if_already_liked(request):
#     user = request.GET.get("user")
#     video_id = request.GET.get("video_id")
#     video = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#     count = Likes.objects.filter(user_id=user, video_model_id=video).count()
#     if count > 0:
#         return JsonResponse({'code':201, 'message':'already liked'})
#     else:
#         return JsonResponse({'code':200, 'message':'allow like'})

# def check_if_already_reviewed(request):
#     user = request.GET.get("user")
#     video_id = request.GET.get("video_id")
#     video = list(VideosModel.objects.filter(url=video_id).values('id'))[0]['id']
#     count = Review.objects.filter(user_id=user, video_model_id=video).count()
#     print(count)
#     if count > 0:
#         return JsonResponse({'code':201, 'message':'already reviewed'})
#     else:
#         return JsonResponse({'code':200, 'message':'allow review'})



# def save_to_playlist(request):
#     if request.method == 'POST':
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         user = ds['user']
#         playlist = ds['playlist']
#         count = SaveToPlaylist.objects.filter(user_id=user,playlist_id=playlist).all().count()
#         if count > 0:
#             return JsonResponse({'code':300, 'message':'already saved'})
#         obj= SaveToPlaylist.objects.create(user_id=user,playlist_id=playlist)
#         if obj:
#             return JsonResponse({'code':200, 'message':'success'})
#         else:
#             return JsonResponse({'code':500, 'message':'server error'})
#     elif request.method == "GET":
#         user = request.GET.get('user')
#         ids = SaveToPlaylist.objects.filter(user_id=user).values_list('playlist_id')
#         # res = list(PlayLists.objects.filter(id__in=ids).values())
#         res = list(PlayLists.objects.filter(id__in=ids).values().annotate(videos=Count('playlists_videos')))
#         return JsonResponse(res, safe=False)
#     else:
#         return JsonResponse({'code':500, 'message':'Bad Request'})


# def check_playlist_if_already_saved(request):
#     user = request.GET.get('user')
#     playlist = request.GET.get('playlist')
#     count = SaveToPlaylist.objects.filter(user_id=user,playlist_id=playlist).all().count()
#     if count > 0:
#         return JsonResponse({
#             'code':200,
#             "msg":"already saved"
#         })
#     else:
#         return JsonResponse({
#             'code':300,
#             "msg":"not saved"
#         })
