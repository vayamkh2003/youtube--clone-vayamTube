from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Channel, Video, Comment, UserProfile

# Create your views here.
def home(request):
    # Optimize query with select_related and pagination
    videos_list = Video.objects.select_related('channel', 'user').all().order_by('-upload_time')
    paginator = Paginator(videos_list, 12)  # Show 12 videos per page
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)

    return render(request, "home.html", {"videos": videos})

def channel(request, username, pk):
    try:
        user = get_object_or_404(User, username=username)
        channel = get_object_or_404(Channel, user=user, id=pk)
        videos_list = Video.objects.filter(channel=channel).select_related('channel', 'user').order_by('-upload_time')
        paginator = Paginator(videos_list, 12)  # Show 12 videos per page
        page_number = request.GET.get('page')
        videos = paginator.get_page(page_number)

        if request.method == "POST":
            action = request.POST.get('subscribe')
            if action == 'unsubscribe':
                channel.subscribers.remove(request.user)
                messages.success(request, f"Unsubscribed from {channel.name}")
            else:
                channel.subscribers.add(request.user)
                messages.success(request, f"Subscribed to {channel.name}")
            channel.save()

        return render(request, "channel.html", {"channel": channel, "videos": videos})
    except Exception as e:
        messages.error(request, "An error occurred while loading the channel.")
        return redirect('home')

def video(request, pk):
    try:
        video = get_object_or_404(Video.objects.select_related('channel', 'user'), id=pk)
        return render(request, "video.html", {"video": video})
    except Exception as e:
        messages.error(request, "Video not found.")
        return redirect('home')

def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        email = request.POST.get('email')

        if form.is_valid():
            user = form.save()
            # Create UserProfile
            UserProfile.objects.create(user=user, email=email)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "create_user.html", {'form': form})

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    else:
        return render(request, "login.html")

def custom_logout(request):
    logout(request)
    return redirect('home')

def create_channel(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            name = request.POST["channelName"]
            pfp = request.FILES.get('channel_pfp')

            if name and pfp:
                channel = Channel(user=request.user, name=name, profile_picture=pfp)
                channel.save()

                return redirect('home')
        else:
            return render(request, 'create_channel.html')
    
    else:
        return redirect('login')
    
    return render(request, 'create_channel.html')

def upload_video(request):
    if request.user.is_authenticated:
        channels = Channel.objects.filter(user=request.user)

        if request.method == "POST":
            try:
                channel_id = request.POST.get('video_channel')
                channel = get_object_or_404(Channel, id=channel_id, user=request.user)

                video_file = request.FILES.get('video_file')
                title = request.POST.get('video_title')
                description = request.POST.get('video_description')
                thumbnail = request.FILES.get('video_thumbnail')
                category = request.POST.get('video_category')

                # Server-side validation
                MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200 MB
                MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5 MB

                if not (channel and video_file and title and thumbnail):
                    messages.error(request, "Please fill in all required fields.")
                elif hasattr(video_file, 'content_type') and not str(video_file.content_type).startswith('video'):
                    messages.error(request, "Uploaded file is not a valid video type.")
                elif video_file.size > MAX_VIDEO_SIZE:
                    messages.error(request, "Video file too large (max 200MB).")
                elif thumbnail and (hasattr(thumbnail, 'content_type') and not str(thumbnail.content_type).startswith('image')):
                    messages.error(request, "Thumbnail must be an image file.")
                elif thumbnail and thumbnail.size > MAX_IMAGE_SIZE:
                    messages.error(request, "Thumbnail too large (max 5MB).")
                else:
                    video = Video(
                        user=request.user, 
                        channel=channel, 
                        video_file=video_file, 
                        title=title, 
                        description=description, 
                        thumbnail=thumbnail,
                        category=category
                    )
                    video.save()
                    messages.success(request, "Video uploaded successfully!")
                    return redirect('home')
            except Exception as e:
                messages.error(request, "An error occurred while uploading the video.")
        else:
            return render(request, "upload_video.html", {"channels": channels})

    else:
        return redirect('login')

    return render(request, "upload_video.html", {"channels": channels})

def searched(request):
    if request.method == "POST":
        searched_value = request.POST.get('s')
        if searched_value:
            videos_list = Video.objects.filter(title__icontains=searched_value).select_related('channel', 'user').order_by('-upload_time')
            paginator = Paginator(videos_list, 12)
            page_number = request.GET.get('page')
            videos = paginator.get_page(page_number)
            channels = Channel.objects.filter(name__icontains=searched_value)
            return render(request, "searched.html", {"videos": videos, "channels": channels, "search_term": searched_value})
        else:
            messages.warning(request, "Please enter a search term.")
            return redirect('home')
    return redirect('home')

def video_view(request, pk):
    if request.user.is_authenticated:
        try:
            video = get_object_or_404(Video, id=pk)
            if not video.view.filter(id=request.user.id).exists():
                video.view.add(request.user)
            return redirect('video', pk=pk)
        except Exception as e:
            messages.error(request, "An error occurred while updating view count.")
            return redirect('video', pk=pk)
    else:
        return redirect('login')

def video_like(request, pk):
    if request.user.is_authenticated:
        try:
            video = get_object_or_404(Video, id=pk)
            if not video.dislikes.filter(id=request.user.id).exists():
                if video.likes.filter(id=request.user.id).exists():
                    video.likes.remove(request.user)
                else:
                    video.likes.add(request.user)
            return redirect('video', pk=pk)
        except Exception as e:
            messages.error(request, "An error occurred while processing your like.")
            return redirect('video', pk=pk)
    else:
        return redirect('login')

def video_dislike(request, pk):
    if request.user.is_authenticated:
        video = Video.objects.get(id=pk)

        if not video.likes.filter(id=request.user.id):
            if video.dislikes.filter(id=request.user.id):
                video.dislikes.remove(request.user)
            else:
                video.dislikes.add(request.user)
        
        return redirect('video', pk=pk)
    
    else:
        return redirect('login')

def video_comment(request, pk):
    if request.user.is_authenticated:
        video = Video.objects.get(id=pk)

        if request.method == "POST":
            comment_text = request.POST['comment']
            comment = Comment.objects.create(user=request.user, video=video, text=comment_text)

        return redirect('video', pk=pk)

    else:
        return redirect('login')
