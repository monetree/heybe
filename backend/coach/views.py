from .models import (
    coachRegister, 
    Otp, 
    CoachBio, 
    Video, 
    Playlist, 
    PlayListVideos, 
    Associated,
    ToggleSections,
    Review,
    Testimonial,
    Comments,
    NoOfPlayedTimes,
    NoOfUsersWhoHaveSeen,
    AvgViewTime,
    Likes,
    VideoAccessForPrivateVideos
)

from user.models import userRegister
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import FileSystemStorage
from .utils import send_mail
import random
from django.db.models import Q, Sum, Count
import json
# from .serializers import MainVideoSerializer
# from django.db.models import Count, Q
# from django.core.files.storage import FileSystemStorage

class CoachAuth:
    def coach_register(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            name= ds['name']
            email=ds['email']
            mobile=ds['phone']
            password=ds['password']

            count_email = coachRegister.objects.filter(email=email).count()
            count_mobile = coachRegister.objects.filter(mobile=mobile).count()

            if count_email > 0:
                return JsonResponse({"code":422,"msg":"duplicate email"})
            if count_mobile > 0:
                return JsonResponse({"code":423,"msg":"duplicate mobile"})

            obj= coachRegister.objects.create(approved=False, name=name,email=email,mobile=mobile, password=make_password(password, salt=None, hasher='default'))
            if obj:
                id = list(coachRegister.objects.filter(email=email).values('id'))[0]['id']
                return JsonResponse({'code':200, 'message':'success', 'id':id, 'email': email, 'name':name})
        else:
            coach_id = request.GET.get("coach_id")
            res = list(coachRegister.objects.filter(id=coach_id).values('name', 'id'))
            return JsonResponse(res, safe=False)


    def coach_login(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            password=ds['password']

            count= coachRegister.objects.filter(email=email).count()
            if count > 0:
                hashed_password = list(coachRegister.objects.filter(email=email).values('password'))[0]['password']
                match = check_password(password, hashed_password)
                if not match:
                    return JsonResponse({ 'code':400, 'message':'Invalid credentials'})
                id = list(coachRegister.objects.filter(email=email).values('id'))[0]['id']
                name = list(coachRegister.objects.filter(email=email).values('name'))[0]['name']
                return JsonResponse({'code':200, 'message':'success', 'id':id, 'email': email, 'name':name})
            else :
                return JsonResponse({ 'code':400, 'message':'Invalid credentials'})
        else:
            return JsonResponse({'code':500, 'message':'Internal server error'})

    def coach_forgot_password(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            count= coachRegister.objects.filter(email=email).count()
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

    def coach_verify_otp(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            otp = ds['otp']
            # email = ds['email']
            count= Otp.objects.filter( otp=otp).count()
            if count > 0:
                return JsonResponse({'code':200, 'message':'verify otp'})
            else:
                return JsonResponse({'code':400, 'message':'otp is wrong'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})

    def coach_change_password(request):
        if request.method == 'POST':
            data = request.body
            convert = data.decode("utf-8")
            ds = json.loads(convert)
            email=ds['email']
            password=ds['password']
            obj= coachRegister.objects.filter(email=email).update(password=make_password(password, salt=None, hasher='default'))
            if obj:
                return JsonResponse({'code':200, 'message':'success'})
            else:
                return JsonResponse({'code':500, 'message':'Internal server error'})
        else:
            return JsonResponse({'code':500, 'message':'Bad Request'})

def likes(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        like        = ds['like']
        coach_id    = ds['coach_id']
        user_id     = ds['user_id']
        video_id    = ds['video_id']
        count = Likes.objects.filter(user_id=user_id, video_id=video_id).count()
        if count > 0:
            count = Likes.objects.filter(user_id=user_id, video_id=video_id).update(like=like)
            return JsonResponse({"code": 200, "msg": "success"})

        obj = Likes.objects.create(user_id=user_id, coach_id=coach_id, like=like, video_id=video_id)
        if obj:
            return JsonResponse({"code": 200, "msg": "success"})
        else:
            return JsonResponse({"code":500, "msg": "Internal server error"})
    else:
        user_id = request.GET.get("user_id")
        video_id = request.GET.get("video_id")
        liked = list(Likes.objects.filter(video_id=video_id, user_id=user_id).values())
        if liked:
            liked = liked[0]["like"]
        else:
            liked = 0
        likes = Likes.objects.filter(video_id=video_id, like=1).count()
        dislikes = Likes.objects.filter(video_id=video_id, like=2).count()
        res = {"likes": likes, "dislikes": dislikes, "liked": liked}
        return JsonResponse(res, safe=False)

def no_of_playlists_the_video_is_in(request):
    video_id = request.GET.get("video_id")
    res = list(PlayListVideos.objects.filter(video_id=video_id).values().annotate(total=Count('playlist_id')))
    return JsonResponse(res, safe=False)

def avg_view_time(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        video_id = ds['video_id']
        coach_id = ds['coach_id']
        user_id = ds['user_id']
        view_time = ds["view_time"]

        count = list(AvgViewTime.objects.filter(video_id=video_id, user_id=user_id).values())
        if len(count) > 0:
            currnt_view_time = count[0]["avg_view_time"]
            view_time = float(view_time) + float(currnt_view_time)
            count = AvgViewTime.objects.filter(video_id=video_id,user_id=user_id).update(avg_view_time=view_time)
            count = list(AvgViewTime.objects.filter(video_id=video_id).values().annotate(total_watched=Sum('user_id')))
        else:
            if avg_view_time == 0:
                avg_view_time = 1
            obj = AvgViewTime.objects.create(video_id=video_id, coach_id=coach_id, user_id=user_id, avg_view_time=float(view_time) )
            count = list(AvgViewTime.objects.filter(video_id=video_id).values().annotate(total_watched=Sum('user_id')))
  
        return JsonResponse({"code": 200, "msg": "success"})

    else:
        video_id = request.GET.get("video_id")
        res = list(AvgViewTime.objects.filter(video_id=video_id).values().annotate(total_watched=Sum('user_id')))
        total_times = []
        for i in res:
            total_times.append(i["avg_view_time"])
        return JsonResponse({"avg_watch_time": sum(total_times)/len(total_times)}, safe=False)

def no_of_users_who_have_seen(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        video_id = ds['video_id']
        coach_id = ds['coach_id']
        user_id = ds['user_id']
        count = list(NoOfUsersWhoHaveSeen.objects.filter(video_id=video_id, user_id=user_id).values())
        if len(count) > 0:
            obj = NoOfUsersWhoHaveSeen.objects.filter(video_id=video_id).count()
        else:
            obj = NoOfUsersWhoHaveSeen.objects.create(video_id=video_id, coach_id=coach_id, user_id=user_id)
            obj = NoOfUsersWhoHaveSeen.objects.filter(video_id=video_id).count()

        return JsonResponse({"count": obj})
    else:
        video_id = request.GET.get("video_id")
        res = list(NoOfUsersWhoHaveSeen.objects.filter(video_id=video_id).values())
        return JsonResponse(res, safe=False) 

def no_of_played_times(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        video_id = ds['video_id']
        coach_id = ds['coach_id']
        user_id = ds['user_id']
            
        count = list(NoOfPlayedTimes.objects.filter(video_id=video_id).values())
        if len(count) > 0:
            played_time = count[0]["no_of_played_times"]
            played_time = played_time+1
            obj = NoOfPlayedTimes.objects.filter(video_id=video_id).update(no_of_played_times=played_time)
        else:
            obj = NoOfPlayedTimes.objects.create(no_of_played_times=1, video_id=video_id, coach_id=coach_id, user_id=user_id)
        return JsonResponse(count, safe=False)

    else:
        video_id = request.GET.get("video_id")
        res = list(NoOfPlayedTimes.objects.filter(video_id=video_id).values())
        return JsonResponse(res, safe=False)


def video_access(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        user = ds["user"]
        video = ds["video"]
        count = VideoAccessForPrivateVideos.objects.filter(user_id=int(user), video_id=int(video)).count()
        if count > 0:
            return JsonResponse({"code": 200, "msg": "success"})

        VideoAccessForPrivateVideos.objects.create(user_id=int(user), video_id=int(video))
        return JsonResponse({"code": 200, "msg": "success"})
    elif request.method == "PUT":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        user = ds["user"]
        video = ds["video"]
        VideoAccessForPrivateVideos.objects.filter(user_id=int(user), video_id=int(video)).delete()
        return JsonResponse({"code": 200, "msg": "success"})

    else:
        video_id = request.GET.get("video_id")
        res = list(VideoAccessForPrivateVideos.objects.filter(video=video_id).values())
        return JsonResponse(res, safe=False)

def testimonial(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        coach_id = ds["coach_id"]
        user_id = ds["user_id"]
        testimonial = ds["testimonial"]
        count = Testimonial.objects.filter(user_id=user_id, coach_id=coach_id).count()
        if count > 0:
            Testimonial.objects.filter(user_id=user_id, coach_id=coach_id).update(testimonial=testimonial)
        else:
            Testimonial.objects.create(user_id=user_id, testimonial=testimonial, coach_id=coach_id)
        return JsonResponse({"code":200, "msg":"succss"})
    else:
        coach_id = request.GET.get("coach_id")
        res = list(Testimonial.objects.filter(coach_id=coach_id).values())
        return JsonResponse(res, safe=False)

def comments(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        comment     = ds["comment"]
        coach_id    = ds["coach_id"]
        user_id     = ds["user_id"]
        video_id    = ds["video_id"]
        Comments.objects.create(user_id=user_id, video_id=video_id, coach_id=coach_id, comment=comment)
        return JsonResponse({"code":200, "msg": "success"})
    else:
        video_id = request.GET.get("video_id")
        if video_id:
            res = list(Comments.objects.filter(video_id=video_id).values("user_id__name","comment", "coach_id", "user_id", "video_id"))
        else:
            res = list(Comments.objects.values("user_id__name","comment", "coach_id", "user_id", "video_id"))
        return JsonResponse(res, safe=False)

def review(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        coach_id = ds["coach_id"]
        user_id = ds["user_id"]
        video_id = ds["video_id"]
        rating = ds["rating"]
        count = Review.objects.filter(user_id=user_id, video_id=video_id).count()
        if count > 0:
            Review.objects.filter(user_id=user_id, video_id=video_id).update(rating=rating)
        else:
            Review.objects.create(user_id=user_id, video_id=video_id, rating=rating, coach_id=coach_id)
        return JsonResponse({"code":200, "msg":"succss"})
        
    else:
        video_id = request.GET.get("video_id")
        coach_id = request.GET.get("coach_id")
        if video_id:
            res = list(Review.objects.filter(video_id=video_id).values())
        elif coach_id:
            res = list(Review.objects.filter(coach_id=coach_id).values())
        else:
            res = list(Review.objects.values())
        return JsonResponse(res, safe=False)

def handle_toggle_section(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        coach_id = ds["coach_id"]
        bio  = ds['bio']
        workout  = ds['workout']
        playlist  = ds['playlist']
        statistics  = ds['statistics']
        
        count = ToggleSections.objects.filter(coach_id=coach_id).count()
        if count > 0:
            ToggleSections.objects.filter(coach_id=coach_id).update(bio=bio, workout=workout, playlist=playlist, statistics=statistics)
        else:
            ToggleSections.objects.create(coach_id=coach_id, bio=bio, workout=workout, playlist=playlist, statistics=statistics)
        return JsonResponse({"code":200, "msg":"success"})
    else:
        coach_id = request.GET.get("coach_id")
        res = list(ToggleSections.objects.filter(coach_id=coach_id).values())
        return JsonResponse(res, safe=False)

def coach_bio(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        bio=ds['bio']
        logo=ds['logo']
        banner=ds["banner"]
        coach_id=ds['id']
        count = CoachBio.objects.filter(coach_id=coach_id).count()
        if count > 0:
            return JsonResponse({"code":200,"msg":"success"})
        obj = CoachBio.objects.create(coach_id=coach_id, bio=bio, logo=logo, banner=banner)
        if obj:
            return JsonResponse({"code":200,"msg":"success"})
        else:
            return JsonResponse({"code":500,"msg":"server error"})
    elif request.method == "GET":
        coach_url = request.GET.get('url')
        coach_id = request.GET.get('coach_id')
        coach_name = request.GET.get('name')
        if coach_url:
            obj = CoachBio.objects.filter(coach_id=coach_id).update(url=coach_url)
            if obj:
                return JsonResponse({'code':200, 'message':'success'})
            else:
                return JsonResponse({'code':500, 'message':'Internal server error'})
        if coach_id:
            res = list(CoachBio.objects.filter(coach_id=coach_id).values()[:1])
        elif coach_name:
            res = list(CoachBio.objects.filter(url=coach_name).values()[:1])
            if len(res) == 0:
                res = list(coachRegister.objects.filter(name=coach_name).values()[:1])
                coach_id = res[0]["id"]
                res = list(CoachBio.objects.filter(coach_id=coach_id).values()[:1])
                for i in res:
                    i["name"]=list(coachRegister.objects.filter(id=i["coach_id"]).values('name'))[0]["name"]
                return JsonResponse(res, safe=False)
            for i in res:
                i["name"]=list(coachRegister.objects.filter(id=i["coach_id"]).values('name'))[0]["name"]
        else:
            res = list(CoachBio.objects.filter().values())
            for i in res:
                i["name"]=list(coachRegister.objects.filter(id=i["coach_id"]).values('name'))[0]["name"]
        return JsonResponse(res, safe=False)
    else:
        return JsonResponse({"code":500,"msg":"bad request"})

def get_coach_id(request):
    coach_name = request.GET.get("coach_name")
    res = list(CoachBio.objects.filter(url=coach_name).values())
    if len(res) == 0:
        res = list(coachRegister.objects.filter(name=coach_name).values())
        id = res[0]["id"]
    else:
        id = res[0]["coach_id"]

    return JsonResponse({"coach_id": id}, safe=False)
    
def coach_videos(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)

        title=ds["title"]
        description=ds['description']
        tags=ds['tags']
        equipments=ds["equipments"]
        calories=ds['calories']
        duration=ds["duration"]
        coach_id=ds['id']
        videourl=ds['videourl']
        thumbnailurl=ds['thumbnailurl']
        try:
            accesstype = ds["accesstype"]
        except:
            accesstype = 1
        
        obj = Video.objects.create(
                title=title, 
                description=description, 
                tags=tags, 
                equipments=equipments,
                calories=calories,
                duration=duration,
                coach_id=coach_id,
                video=videourl,
                thumbnail=thumbnailurl,
                accesstype=accesstype
            )
        if obj:
            return JsonResponse({"code":200,"msg":"success"})
        else:
            return JsonResponse({"code":500,"msg":"server error"})
    elif request.method == "GET":
        coach_id = request.GET.get('coach_id')
        count = request.GET.get('count')
        playlist = request.GET.get('playlist_id')
        if coach_id and playlist:
            res = list(PlayListVideos.objects.filter(coach_id=coach_id).order_by("-id").values())
            video_ids = [i["video_id"] for i in res]
            videos = list(Video.objects.filter(~Q(id__in=video_ids)).filter(~Q(video=None)).values())
            return JsonResponse(videos, safe=False)
        if playlist:
            res = list(Video.objects.filter(playlist_id=int(playlist)).filter(~Q(video=None)).order_by("-id").values())
            return JsonResponse(res, safe=False)
        if count:
            res = Video.objects.filter(coach_id=coach_id).filter(~Q(video=None)).count()
            return JsonResponse(res, safe=False)
        res = list(Video.objects.filter(coach_id=coach_id).filter(~Q(video=None)).order_by("-id").values())
        return JsonResponse(res, safe=False)
    elif request.method == "PUT":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        accesstype = ds["accesstype"]
        id = ds["video_id"]
        Video.objects.filter(id=id).update(accesstype=accesstype)
        return JsonResponse({"code":200, "msg": "success"})
    else:
        return JsonResponse({"code":500,"msg":"bad request"})

def videos(request):
    search = request.GET.get("search")
    if search:
        res = list(Video.objects.order_by("-id").filter(
            Q(title__icontains=search) | 
            Q(tags__icontains=search) |
            Q(equipments__icontains=search) |
            Q(description__icontains=search))
        .values())
        return JsonResponse(res, safe=False)
    
    video_id = request.GET.get("video_id")
    playlist_name = None

    if video_id:
        playlist_id = list(Video.objects.filter(id=int(video_id)).filter().values("playlist_id"))[0]["playlist_id"]
        
        if playlist_id:
            playlist_name = list(Playlist.objects.filter(id=playlist_id).values())[0]["title"]
            res = list(Video.objects.filter(playlist_id=int(playlist_id)).filter(~Q(video=None)).filter().order_by("-id").values().order_by("id"))
        else:
            res = list(Video.objects.filter(id=int(video_id)).filter(~Q(video=None)).filter().values().order_by("id"))
        counter = 0
        for i in res:
            counter+=1
            i["serial_no"] = counter

        api = {
            "data": res,
            "playlist_name": playlist_name
        }
        return JsonResponse(api, safe=False)        

    res = list(Video.objects.filter().order_by("-id").values())

    return JsonResponse(res, safe=False)

def public_videos(request):
    res = list(Video.objects.filter(accesstype=1).order_by("-id").values())
    return JsonResponse(res, safe=False)

def allowed_videos(request):
    user_id = request.GET.get("user_id")
    res = list(VideoAccessForPrivateVideos.objects.filter(user_id=user_id).values('video_id'))
    if len(res) > 0:
        ids = [i["video_id"] for i in res]
        res = list(Video.objects.filter(id__in=ids).values())
        return JsonResponse(res, safe=False)
    else:
        return JsonResponse([], safe=False)

def coach_playlist(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)

        title=ds["title"]
        description=ds['description']
        tags=ds['tags']
        duration=ds["duration"]
        coach_id=ds['id']
        thumbnailurl=ds['thumbnailurl'],
        level=ds["level"]
        associated_users=ds["associated_users"]
        if associated_users == "null":
            associated_users = None
        
        obj = Playlist.objects.create(
                title=title, 
                description=description, 
                tags=tags, 
                duration=duration,
                coach_id=coach_id,
                thumbnail=thumbnailurl,
                level=level
            )

        if obj:
            if associated_users:
                last_inserted_id = list(Playlist.objects.values().order_by('-id'))[0]["id"]
                for i in associated_users:
                    count = Associated.objects.filter(playlist_id=last_inserted_id, user_id=int(i)).count()
                    if count == 0:
                        Associated.objects.create(
                            playlist_id = int(last_inserted_id),
                            user_id = int(i)
                        )
            return JsonResponse({"code":200,"msg":"success"})
        else:
            return JsonResponse({"code":500,"msg":"server error"})
    elif request.method == "GET":
        coach_id = request.GET.get('coach_id')
        res = list(Playlist.objects.filter(coach_id=coach_id).values())
        for i in res:
            i["workouts"] = list(Video.objects.filter(coach_id=coach_id, playlist_id=i["id"]).order_by("-id").values('id'))
        return JsonResponse(res, safe=False)
    else:
        return JsonResponse({"code":500,"msg":"bad request"})

def associated_users(request):
    if request.method == 'POST':
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        user_id=ds['user_id']
        playlist_id=ds['playlist_id']
        if not user_id:
            res = list(Associated.objects.filter(playlist_id=int(playlist_id)).values().annotate(count=Count('user_id')))
            print(res)
            return JsonResponse(res, safe=False)
        count = Associated.objects.filter(playlist_id=int(playlist_id), user_id=int(user_id)).count()
        if count == 0:
            Associated.objects.create(
                playlist_id = int(playlist_id),
                user_id = int(user_id)
            )
            return JsonResponse({"code":200,"msg":"success"})
        return JsonResponse({"code":200,"msg":"success"})
    elif request.method == "PUT":
        playlist_id = request.GET.get("playlist_id")
        user_id = request.GET.get("user_id")
        allow = request.GET.get('allow')
        if int(allow) == 0:
            allow = False
        else:
            allow = True

        try:
            Associated.objects.filter(playlist_id=playlist_id, user_id=user_id).update(active=allow)
            return JsonResponse({"code":200,"msg":"success"})
        except:
            return JsonResponse({"code":500,"msg":"Internal server error"})

    elif request.method == "DELETE":
        playlist_id = request.GET.get("playlist_id")
        user_id = request.GET.get("user_id")
        try:
            Associated.objects.filter(playlist_id=playlist_id, user_id=user_id).delete()
            return JsonResponse({"code":200,"msg":"success"})
        except:
            return JsonResponse({"code":500,"msg":"Internal server error"})
            
    elif request.method == 'GET':
        playlist_id = request.GET.get("playlist_id")
        users = list(Associated.objects.filter(playlist_id=playlist_id).values('user_id','active'))
        for i in users:
            user = list(userRegister.objects.filter(id=i["user_id"]).values('name','email'))[0]
            i["name"] = user["name"]
            i["email"] = user["email"]
        return JsonResponse(users, safe=False)
    else:
        return JsonResponse({"code":500, "msg":"bad request"})

def add_to_playlist(request):
    if request.method == "POST":
        data = request.body
        convert = data.decode("utf-8")
        ds = json.loads(convert)
        coach_id= ds['coach_id']
        video_id=ds['video_id']
        playlist_id=ds['playlist_id']

        count = PlayListVideos.objects.filter(coach_id=coach_id,video_id=video_id,playlist_id=playlist_id).count()
        if count > 0:
            return JsonResponse({"code":200,"msg":"success","playlist_id":playlist_id})
        obj = PlayListVideos.objects.create(coach_id=coach_id,video_id=video_id,playlist_id=playlist_id)
        obj2 = Video.objects.filter(id=video_id).update(playlist_id=playlist_id)
        if obj:
            return JsonResponse({"code":200,"msg":"success","playlist_id":playlist_id})
        else:
            return JsonResponse({"code":500,"msg":"server error"})
    else:
        return JsonResponse({"code":500, "msg":"bad request"})


def keywords_equipments(request):
    coach_id = request.GET.get('coach_id')
    obj = list(Video.objects.filter(coach_id=coach_id).values('tags', 'equipments'))
    keywords = []
    equipments = []
    for i in obj:
        keywords.append(eval(i["tags"]))
        equipments.append(eval(i["equipments"]))
    return JsonResponse({"keywords":list(set(sum(keywords, []))), "equipments":list(set(sum(equipments, []))) }, safe=False)

# def video(request):
#     if request.method == "POST":
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         url         = ds['url']
#         coach       = ds['id']
#         title       = ds['title']
#         video_title = ds['video_title']
#         if len(video_title) > 0:
#             title = video_title
#         tags        = ds['tags']
#         level       = ds['level']
#         duration    = ds['duration'].replace("PT","").replace("M",":").replace("S","").replace("H",":")
#         obj = VideosModel.objects.create(
#                 url      = url,
#                 coach_id = coach,
#                 title    = title,
#                 duration = duration,
#                 level    = int(level),
#                 tags     = tags
#             )
#         if obj:
#             return JsonResponse({"code":200, "msg":"success"})
#         else:
#             return JsonResponse({"code":500, "msg":"server error"})

#     if request.method == "GET":
#         video_id = request.GET.get('video_id', None)
#         coach_id = request.GET.get('coach_id', None)
#         playlist = request.GET.get('playlist', None)
#         search = request.GET.get('search', None)
#         if video_id:
#             res = list(VideosModel.objects.filter(url=video_id).values(
#                 'coach__name',
#                 'url','upadated_on',
#                 'title','duration',
#                 'level','tags','views',
#                 'coach','id'
#             ))
#             return JsonResponse(res, safe=False)
#         if coach_id:
#             res = list(VideosModel.objects.filter(coach_id=coach_id).values(
#                 'coach__name',
#                 'url','upadated_on',
#                 'title','duration',
#                 'level','tags','views',
#                 'coach','id'
#             ))
#             return JsonResponse(res, safe=False)
#         if playlist:
#             ids = list(PlayListVideos.objects.filter(playlist_id=playlist).values_list('video_id',flat=True))
#             res = list(VideosModel.objects.filter(id__in=ids).values(
#                 'coach__name',
#                 'url','upadated_on',
#                 'title','duration',
#                 'level','tags','views',
#                 'coach','id'
#             ))
#             return JsonResponse(res, safe=False)
#         if search:
#             res = list(VideosModel.objects.filter(Q(title__icontains=search) | Q(tags__icontains=search)).values(
#                 'coach__name',
#                 'url','upadated_on',
#                 'title','duration',
#                 'level','tags','views',
#                 'coach','id'
#             ))
#             return JsonResponse(res, safe=False)
#         res = list(VideosModel.objects.values(
#             'coach__name',
#             'url','upadated_on',
#             'title','duration',
#             'level','tags','views',
#             'coach','likes'
#         ))
#         return JsonResponse(res, safe=False)
#     if request.method == "DELETE":
#         pass
#     else:
#         return JsonResponse({"code":501, "msg":"bad request"})

# def get_coach_id(request):
#     video_id = request.GET.get("video_id")
#     video_id = request.GET.get('video_id', None)
#     if video_id:
#         coach_id = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         return JsonResponse({"coach_id":coach_id})
#     else:
#         return JsonResponse({"code":400,"msg":"video_id required"})


# def get_similar_videos(request):
#     video_id = request.GET.get('video_id', None)
#     if video_id:
#         coach_id = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         res = list(VideosModel.objects.filter(coach_id=int(coach_id)).values())
#         return JsonResponse(res, safe=False)
#     else:
#         return JsonResponse({"code":400,"msg":"video_id required"})


# def test(request):
#     return JsonResponse({"code":200, "msg":"success"})


# def make_view(request):
#     video_id = request.GET.get('video_id', None)
#     if video_id:
#         view = list(VideosModel.objects.filter(url=video_id).values('views'))[0]['views']
#         update = VideosModel.objects.filter(url=video_id).update(views=int(view)+1)
#         if update:
#             return JsonResponse({"code":200, "msg":"success"})
#         else:
#             return JsonResponse({"code":500, "msg":"server error"})
#     return JsonResponse({"code":400, "msg":"video_id required"})


# def coach_details(request):
#     video_id = request.GET.get('video_id', None)
#     if video_id:
#         coach_id = list(VideosModel.objects.filter(url=video_id).values('coach'))[0]['coach']
#         count = VideosModel.objects.filter(coach_id=coach_id).count()
#         coach_name = list(coachRegister.objects.filter(id=coach_id).values('name'))[0]['name']
#         context = {
#             "name":coach_name,
#             "count":count,
#             "coach":coach_id
#         }
#         return JsonResponse(context, safe=False)
#     else:
#         return JsonResponse({"code":400,"msg":"video_id required"})


# from rest_framework import viewsets
# class MainEmployerViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset =  VideosModel.objects.all()
#     serializer_class = MainVideoSerializer

#     def get_queryset(self):
#         queryset    = VideosModel.objects.all()
#         video_id = self.request.query_params.get('video_id', None)
#         coach_id = self.request.query_params.get('coach_id', None)
#         if video_id is not None:
#             queryset = queryset.filter(id=video_id)
#         if coach_id is not None:
#             queryset = queryset.filter(coach_id=coach_id)
#         return queryset


# def delete_video(request):
#     video_id = request.GET.get("video_id")
#     if video_id:
#         obj = VideosModel.objects.filter(id=video_id).delete()
#         if obj:
#             return JsonResponse({"code":200, "msg":"success"})
#         else:
#             return JsonResponse({"code":500, "msg":"server error"})
#     else:
#         return JsonResponse({"code":400, "msg":"video_id required"})


# def playlists(request):
#     if request.method == "POST":
#         playlist = request.POST['playlist']
#         level = request.POST['level']
#         coach = request.POST['coach']
#         thumb = request.FILES['thumb']
#         if thumb:
#             fs = FileSystemStorage()
#             filename = fs.save(thumb.name, thumb)
#             uploaded_photo_url = fs.url(filename)
#             obj = PlayLists.objects.create(coach_id=int(coach),name=playlist,thumbnail=uploaded_photo_url,difficulty=int(level))
#         else:
#             obj = PlayLists.objects.create(coach_id=int(coach),name=playlist,difficulty=int(level))
        
#         if obj:
#             return JsonResponse({"code":200,"msg":"success"})
#         else:
#             return JsonResponse({"code":500,"msg":"server error"})
#     elif request.method == "GET":
#         coach_id  = request.GET.get('coach_id')
#         if coach_id:
#             res = list(PlayLists.objects.filter(coach_id=coach_id).values('id','name','thumbnail','created_on').annotate(videos=Count('playlists_videos')))
#         else:
#             res = list(PlayLists.objects.values('id','name','thumbnail','created_on').annotate(videos=Count('playlists_videos')))
#         # res = list(PlayListVideos.objects.values('playlist__name','video__url','video__title').annotate(videos=Count('playlist__name')))
#         for i in res:
#             i['thumbnail'] = 'http://' + request.META['HTTP_HOST'] + i['thumbnail']
#         return JsonResponse(res, safe=False)
#     else:
#         return JsonResponse({"code":500, "msg":"bad request"})




# def remove_from_playlist(request):
#     if request.method == "POST":
#         data = request.body
#         convert = data.decode("utf-8")
#         ds = json.loads(convert)
#         coach_id= ds['coach_id']
#         video_id=ds['video_id']
#         playlist_id=ds['playlist_id']
#         obj = PlayListVideos.objects.filter(coach_id=coach_id,video_id=video_id,playlist_id=playlist_id).delete()
#         if obj:
#             return JsonResponse({"code":200,"msg":"success","playlist_id":playlist_id})
#         else:
#             return JsonResponse({"code":500,"msg":"server error"})
#     else:
#         return JsonResponse({"code":500, "msg":"bad request"})

# def add_to_playlist_table(request):
#     coach_id = request.GET.get('coach_id', None)
#     playlist = request.GET.get('playlist', None)
#     ids       = list(PlayListVideos.objects.filter(playlist_id=playlist).values_list('video_id',flat=True))
#     all_video = list(VideosModel.objects.filter(coach_id=coach_id).exclude(id__in=ids).values())
#     return JsonResponse(all_video, safe=False)


# def remove_from_playlist_table(request):
#     coach_id = request.GET.get('coach_id', None)
#     playlist = request.GET.get('playlist', None)
#     ids       = list(PlayListVideos.objects.filter(playlist_id=playlist).values_list('video_id',flat=True))
#     all_video = list(VideosModel.objects.filter(coach_id=coach_id,id__in=ids).values())
#     return JsonResponse(all_video, safe=False)


# def handle_coach_logo(request):
#     if request.method == "POST":
#         coach_id = request.POST['coach']
#         thumb    = request.FILES['logo']

#         fs = FileSystemStorage()
#         filename = fs.save(thumb.name, thumb)
#         uploaded_photo_url = fs.url(filename)

#         count = CoachLogo.objects.filter(coach_id=coach_id).all().count()
#         if count > 0:
#             obj = CoachLogo.objects.filter(coach_id=coach_id).update(logo=uploaded_photo_url)
#         else:
#             obj = CoachLogo.objects.create(logo=uploaded_photo_url,coach_id=coach_id)
#         if obj:
#             return JsonResponse({
#                 "code":200,
#                 "msg":"success"
#             })
#         else:
#             return JsonResponse({
#                 "code":500,
#                 "msg":"server error"
#             })

#     elif request.method == "GET":
#         coach_id = request.GET.get('coach_id')
#         res = list(CoachLogo.objects.filter(coach_id=coach_id).values('logo'))
#         for i in res:
#             i['logo'] = 'http://' + request.META['HTTP_HOST'] + i['logo']
#         return JsonResponse(res, safe=False)


# def handle_coach_banner(request):
#     if request.method == "POST":
#         coach_id = request.POST['coach']
#         thumb    = request.FILES['banner']

#         fs = FileSystemStorage()
#         filename = fs.save(thumb.name, thumb)
#         uploaded_photo_url = fs.url(filename)

#         count = coachBanner.objects.filter(coach_id=coach_id).all().count()
#         if count > 0:
#             obj = coachBanner.objects.filter(coach_id=coach_id).update(banner=uploaded_photo_url)
#         else:
#             obj = coachBanner.objects.create(banner=uploaded_photo_url,coach_id=coach_id)
#         if obj:
#             return JsonResponse({
#                 "code":200,
#                 "msg":"success"
#             })
#         else:
#             return JsonResponse({
#                 "code":500,
#                 "msg":"server error"
#             })

#     elif request.method == "GET":
#         coach_id = request.GET.get('coach_id')
#         res = list(coachBanner.objects.filter(coach_id=coach_id).values('banner'))
#         for i in res:
#             i['banner'] = 'http://' + request.META['HTTP_HOST'] + i['banner']
#         return JsonResponse(res, safe=False)


# def get_coach_name(request):
#     coach_id = request.GET.get('coach_id')
#     res = list(coachRegister.objects.filter(id=coach_id).values('name'))
#     return JsonResponse(res, safe=False)

# def video_series(request):
#     playlist_id = request.GET.get('playlist')
#     ids = list(PlayListVideos.objects.filter(playlist_id=playlist_id).values_list('video_id',flat=True))
#     res = list(VideosModel.objects.filter(id__in=ids).values())
#     return JsonResponse(res, safe=False)

# def check_if_videos_of_same_coach(request):
#     id = request.GET.get('video_id')
#     coach = request.GET.get('coach_id')
#     count = VideosModel.objects.filter(coach_id=coach,id=id).count()
#     if count > 0:
#         return JsonResponse({
#             "code":200,
#             "msg":'allow'
#         })
#     else:
#         return JsonResponse({
#             "code":300,
#             "msg":"not allowed"
#         })


# def get_playlists_by_coach(request):
#     coach = request.GET.get('coach_id')
#     print(coach)
#     res = list(PlayLists.objects.filter(coach_id=coach).values())
#     return JsonResponse(res, safe=False)

# """
# video title
# video duration

# """
# # https://www.googleapis.com/youtube/v3/videos?id=LMVlVI4Jak8&key=AIzaSyD8IX7eL0hyIDos4L9tqZ1RyVpqBL6tNuw&fields=items(id,snippet(channelId,title,categoryId),statistics)&part=snippet
# # https://www.googleapis.com/youtube/v3/videos?id=LMVlVI4Jak8&part=contentDetails,statistics&key=AIzaSyD8IX7eL0hyIDos4L9tqZ1RyVpqBL6tNuw
