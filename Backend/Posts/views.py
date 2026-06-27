from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, SavedPost, PostImage, PostQuestion, Order, Reserve
from Profile.models import Profile
from .serializers import PostSerializer,PostSavedSerializer,PostQuestionSerializer,OrderSerializer,ReservedSerializer, PostImageSerializer
from django.http import Http404
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
import datetime
import jwt
from django.conf import settings
from rest_framework import exceptions
from datetime import date,datetime, timedelta,timezone
import time
import razorpay
import os
import json
from django.utils import timezone
import cloudinary.uploader
from PIL import Image
import io

def compress_image(image_file):
    if image_file == "undefined" or image_file == "null":
        return image_file
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((1920, 1920), Image.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return output
    except Exception as e:
        return image_file

def timesince_calulate(date,time):
    timesince=""
    if(date.today()!=date):
            days=date.today() - date
            if days==1:
                timesince="{} day ago".format(date.today() - date)
            else:
                timesince="{} days ago".format(date.today() - date)
                    
    else:        
        if (datetime.now().hour != time.hour):
            hours=datetime.now().hour-time.hour
            if hours==1:
                timesince="{} hour ago".format(datetime.now().hour-time.hour)
            else:
                timesince="{} hours ago".format(datetime.now().hour-time.hour)
        else:
            minutes=datetime.now().minute-time.minute
            if minutes<=1:
                timesince="{} min ago".format(datetime.now().minute-time.minute)
            else:
                timesince="{} mins ago".format(datetime.now().minute-time.minute)
    return timesince
 
def get_full_post_data(post, myself=None):
    is_reserved = False
    reserve_expire_date = None
    expire_time = None
    
    if myself:
        try:
            reserve = Reserve.objects.filter(reserve_product=post, user=myself).first()
            if reserve and reserve.expire_date >= timezone.now():
                is_reserved = True
                reserve_expire_date = reserve.expire_date.date().strftime("%B %d, %Y")
                expire_time = reserve.expire_date.time()
        except Exception:
            pass

    is_owner = False
    if myself and myself.user_id == post.user.user_id:
        is_owner = True
        
    user = post.user
    save = None
    if myself:
        try:
            save = SavedPost.objects.filter(post=post, user=myself).first()
        except Exception:
            pass

    post_question = PostQuestion.objects.filter(post=post)
    post_images = []
    questions = []
    
    images = PostImage.objects.filter(post=post)
    for img in images:
        post_images.append(img.image)
        
    for que in post_question:
        questions.append({
            'id': que.id,
            'question': que.question,
            'user': que.user.user_id,
            'is_answered': que.is_answered,
            'answer': que.answer
        })

    return {
        'title': post.title,
        'description': post.description,
        'condition': post.condition,
        'id': post.id,
        'price': post.price,
        'category': post.category,
        'subcategory': post.subcategory,
        'color': post.color,
        'date': post.date,
        'is_donate': post.is_donate,
        'user_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_image': user.image,
        'brand': post.brand,
        'address': user.address,
        'phone': user.phone,
        'pincode': user.pincode,
        'email': user.email,
        'genre': post.genre,
        'city': user.city,
        'is_sold': post.is_sold,
        'is_barter': post.is_barter,
        'district': user.district,
        'is_owner': is_owner,
        'is_saved': (save is not None),
        'images': post_images,
        'questions': questions,
        'is_reserved': is_reserved,
        'is_premium': post.is_premium,
        'reserved_expire_date': reserve_expire_date,
        'reserved_expire_time': expire_time,
    }

class PostCreateView(APIView):
    serializer_class=PostSerializer
    def post(self,request):
        request.data["brand"] = request.data["brand"].capitalize()
        post_serializer=PostSerializer(data=request.data)
        imagearray =[]
        if request.data['img1']!="undefined" and  request.data['img1']!="null":
            compressed_img1 = compress_image(request.data['img1'])
            upload_data = cloudinary.uploader.upload(compressed_img1,folder="post")
            imagearray.append(upload_data['public_id'])
        if request.data['img2']!="undefined" and  request.data['img2']!="null":
            compressed_img2 = compress_image(request.data['img2'])
            upload_data = cloudinary.uploader.upload(compressed_img2,folder="post")
            imagearray.append(upload_data['public_id'])
        if request.data['img3']!="undefined" and  request.data['img3']!="null":
            compressed_img3 = compress_image(request.data['img3'])
            upload_data = cloudinary.uploader.upload(compressed_img3,folder="post")
            imagearray.append(upload_data['public_id'])
        if request.data['img4']!="undefined" and request.data['img4']!="null":
            compressed_img4 = compress_image(request.data['img4'])
            upload_data = cloudinary.uploader.upload(compressed_img4,folder="post")   
            imagearray.append(upload_data['public_id']) 
        try:    
            user=Profile.objects.get(user_id=request.data['user'])
        except:
            for img in imagearray:    
                cloudinary.uploader.destroy(img,invalidate=True)    
        if(user.city=="" or user.district=="" or user.address=="" or user.pincode=="" or user.phone==""):
            for img in imagearray:    
                cloudinary.uploader.destroy(img,invalidate=True)
            return Response("Please complete your profile",status=status.HTTP_204_NO_CONTENT)
        if post_serializer.is_valid() and post_serializer.is_valid_form(request.data):
            post_serializer.save()
            is_premium = request.data.get("is_premium")
            if is_premium == "true" or is_premium is True:
                Profile.objects.filter(user_id = request.data["user"]).update(coins = max(0,user.coins-250));
            else:
                Profile.objects.filter(user_id = request.data["user"]).update(coins = user.coins+50);
            
            # Fetch full post data to return
            created_post = Post.objects.get(id=post_serializer.instance.id)
            for img in imagearray:
                try:
                    new_image=PostImage.objects.create(post=created_post,image=img)
                    PostImageSerializer(new_image)
                except:
                    for img in imagearray:    
                        cloudinary.uploader.destroy(img,invalidate=True)    
                    return Response("Something went wrong", status=status.HTTP_400_BAD_REQUEST)    
            data = get_full_post_data(created_post, user)
            return Response(data,status=status.HTTP_201_CREATED)
        for img in imagearray:    
            cloudinary.uploader.destroy(img,invalidate=True)    
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllBrands(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        data = Post.objects.order_by('brand').values_list('brand', flat=True).distinct()
        return Response(data,status=status.HTTP_200_OK)  

class PostEditView(APIView):
    serializer_class=PostSerializer
    # permission_classes=[IsAuthenticated]
    def put(self,request):
        post_id = request.data['id']
        
        try:
            user_data=Profile.objects.get(user_id=request.data['user'])
        except Profile.DoesNotExist:
            return Response("user doesn't exists",status=status.HTTP_204_NO_CONTENT)  
        try:
            post=Post.objects.get(user=request.data['user'],id=post_id)   
        except Post.DoesNotExist:
             return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT) 

        post_update_serializer=PostSerializer(post,data=request.data)  
        if post_update_serializer.is_valid() and post_update_serializer.is_valid_form(request.data):
            post_update_serializer.save()
            imagearray = []
            if 'img1' in request.data and request.data['img1'] != "undefined" and request.data['img1'] != "null":
                compressed_img1 = compress_image(request.data['img1'])
                upload_data = cloudinary.uploader.upload(compressed_img1, folder="post")
                imagearray.append(upload_data['public_id'])
            if 'img2' in request.data and request.data['img2'] != "undefined" and request.data['img2'] != "null":
                compressed_img2 = compress_image(request.data['img2'])
                upload_data = cloudinary.uploader.upload(compressed_img2, folder="post")
                imagearray.append(upload_data['public_id'])
            if 'img3' in request.data and request.data['img3'] != "undefined" and request.data['img3'] != "null":
                compressed_img3 = compress_image(request.data['img3'])
                upload_data = cloudinary.uploader.upload(compressed_img3, folder="post")
                imagearray.append(upload_data['public_id'])
            if 'img4' in request.data and request.data['img4'] != "undefined" and request.data['img4'] != "null":
                compressed_img4 = compress_image(request.data['img4'])
                upload_data = cloudinary.uploader.upload(compressed_img4, folder="post")
                imagearray.append(upload_data['public_id'])

            for image in imagearray:
                postimage = PostImage(post=post, image=image)
                postimage.save()
            
            is_premium = request.data.get("is_premium")
            if is_premium == "true" or is_premium is True:
                Profile.objects.filter(user_id = request.data["user"]).update(coins = max(0,user_data.coins-300));
            
            # Fetch full post data to return
            updated_post = Post.objects.get(id=post.id)
            data = get_full_post_data(updated_post, user_data)
            return Response(data,status=status.HTTP_200_OK)
        return Response(post_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class PostDeleteView(APIView):
    serializer_class=PostSerializer
    def delete(self,request):
        authorization_header = request.headers.get('Authorization')
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired.')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing.')
        post_id=request.GET['id']
        try:
            user_data=Profile.objects.get(user_id=payload['user_id'])
        except Profile.DoesNotExist:
            return Response("user doesn't exists",status=status.HTTP_204_NO_CONTENT)  
        try:
            post=Post.objects.get(user=payload['user_id'],id=post_id)   
        except Post.DoesNotExist:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT)

        try:
            Post.objects.filter(user=payload['user_id'],id=post_id).delete()
            return Response("post deleted successfully.",status=status.HTTP_200_OK)
        except:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT)

class PostUserRetriveView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header == None:
            raise exceptions.AuthenticationFailed('Authentication credentials were not provided.')
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired.')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing.')

        user = Profile.objects.filter(user_id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found.')

        posts=Post.objects.filter(user=payload['user_id'])
        data=[]
        for post in posts:
            temp={}
            post_images=[]
            questions=[]
            images=PostImage.objects.filter(post=post.id)
            for img in images:
                post_images.append(img.image)
            question=PostQuestion.objects.filter(post=post.id)
            for que in question:
                answered_timesince=""
                if(que.is_answered):
                    if(que.answered_date=="" or que.answered_time=="" or que.answer==""):
                        return Response("Invalid data",status=status.HTTP_400_BAD_REQUEST)
                    answered_timesince= timesince_calulate(que.answered_date,que.answered_time) 
                obj={}
                obj['id']=que.id
                obj['question']=que.question
                obj['timesince']=timesince_calulate(que.date,que.time)
                obj['user_id']=que.user.user_id
                obj['is_answered']=que.is_answered
                obj['answered_timesince']=answered_timesince
                obj['answer']=que.answer
                questions.append(obj)
            # 
            save=SavedPost.objects.filter(post=post.id,user=payload['user_id'])
            temp['title']=post.title
            temp['author']=post.author
            temp['description']=post.description
            temp['genre']=post.genre
            temp['id']=post.id
            temp['is_sold']=post.is_sold
            temp['price']=post.price
            temp['category']=post.category
            temp['timesince']=timesince_calulate(post.date,post.time)
            temp['is_donate']=post.is_donate
            temp['is_barter']=post.is_barter
            temp['is_saved']=(save!=None)
            temp['images']=post_images
            temp["is_premium"] = post.is_premium
            temp['questions']=questions
            data.append(temp) 
        return Response(data,status=status.HTTP_200_OK)

class SinglePostRetriveView(APIView):
    permission_classes = [AllowAny]
    serializer_class=PostSerializer
    def get(self,request):
        authorization_header = request.headers.get('Authorization')
        payload = None
        myself = None
        reserved = None
        reserved_date = None
        is_reserved = False
        expire_date = None
        expire_time = None
        reserve_expire_date = None
        post_id=request.GET['id']
        try:
            post = Post.objects.get(id=post_id)
        except: 
            return Response("post doesn't exist",status=status.HTTP_204_NO_CONTENT)
        if authorization_header:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
            myself = Profile.objects.filter(user_id=payload['user_id']).first()
            if myself is None:
                raise exceptions.AuthenticationFailed('User not found.')
            try:
                reserve=Reserve.objects.get(reserve_product=post_id,user=myself)
                if(reserve.expire_date < timezone.now()):
                    is_reserved=False
                else:
                    is_reserved = True
                    expire_date=reserve.expire_date.date()   
                    expire_time = reserve.expire_date.time() 
                    if expire_date:
                        reserve_expire_date = expire_date.strftime("%B %d, %Y")
            except:
                reserve = None
           

       
        data = get_full_post_data(post, myself)
        return Response(data,status=status.HTTP_200_OK)



class PostRetriveView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        category = request.GET['category']
        subcategory = request.GET['subcategory']
        condition = request.GET['condition']
        state = request.GET['state']
        color = request.GET['color']
        minPrice = request.GET['min']
        maxPrice = request.GET['max']
        brand = request.GET['brand']
        is_barter = request.GET['barter']
        sort = request.GET['sort']
        is_donate = request.GET['donate']
        posts = None
        if(sort=="lowest"):
            posts=Post.objects.all().order_by('price')
        elif(sort=="highest"):
            posts=Post.objects.all().order_by('-price')   
        elif(sort=="new"):
            posts=Post.objects.all().order_by('-date','-time')
        else:
            posts=Post.objects.all()    
        
        temp_data=[]
        data = []
        
        for post in posts:
            if category!="Any" and post.category != category:
                continue
            if subcategory!="Any" and post.subcategory != subcategory:
                continue
            if len(brand)>0 and post.brand not in brand:
                continue
            if state!="Any" and post.is_sold == False:
                continue
            if len(color)>0 and post.color not in color:
                continue
            if len(condition)>0 and post.condition not in condition:
                continue 
            if maxPrice!="0" and (post.price < int(minPrice) or post.price > int(maxPrice) ):
                continue    
            if is_barter=="true" and post.is_barter == False :
                continue
            if is_donate=="true" and post.is_donate == False :
                continue
            post_images=[]
            images=PostImage.objects.filter(post=post.id)
            for img in images:
                post_images.append(img.image)
            temp={}
            temp['title']=post.title
            temp['genre']=post.genre
            temp['id']=post.id
            temp['price']=post.price
            temp['brand']=post.brand
            temp['is_donate'] = post.is_donate
            temp['is_barter'] = post.is_barter
            temp["is_premium"] = post.is_premium
            # temp['is_owner']=(user.user_id==payload['user_id'])
            temp['image']=post_images[0] if post_images else ""
            temp_data.append(temp)
        for  item in temp_data:
            if item['is_premium']:
                data.append(item)
        for  item in temp_data:
            if not item['is_premium']:
                data.append(item)        
        return Response(data,status=status.HTTP_200_OK)



class PostSavedView(APIView):
    permission_classes = [AllowAny]
    serializer_class=PostSavedSerializer
    def post(self,request):
        post_id=request.data['post']
        user_id=request.data['user']
        verb=request.GET['verb']
        if verb=="save":
            post_saved_serializer=PostSavedSerializer(data=request.data)
            try:
                user_data=Profile.objects.get(user_id=user_id)
            except Profile.DoesNotExist:
                return Response("user doesn't exists",status=status.HTTP_400_BAD_REQUEST)  
            try:
                post=Post.objects.get(id=post_id)   
            except Post.DoesNotExist:
                return Response("post doesn't exists",status=status.HTTP_400_BAD_REQUEST)
            
            if SavedPost.objects.filter(post=post_id, user=user_id).exists():
                return Response("Post already saved",status=status.HTTP_200_OK)
            
            if post_saved_serializer.is_valid():
                post_saved_serializer.save()
                return Response("saved",status=status.HTTP_200_OK)
            return Response(post_saved_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif verb=="unsave":
            try:
                user_data=Profile.objects.get(user_id=user_id)
            except Profile.DoesNotExist:
                return Response("user doesn't exists",status=status.HTTP_400_BAD_REQUEST)  
            try:
                post_exists=Post.objects.filter(id=post_id).exists()
                if not post_exists:
                     return Response("post doesn't exists",status=status.HTTP_400_BAD_REQUEST)
            except:
                 pass

            try:
                saved_post=SavedPost.objects.get(user=user_id,post=post_id)   
                saved_post.delete()
                return Response("unsaved.",status=status.HTTP_200_OK)
            except SavedPost.DoesNotExist:
                return Response("post is already unsaved",status=status.HTTP_200_OK)
            except:
                return Response("Something went wrong",status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("incorrect verb",status=status.HTTP_400_BAD_REQUEST)

class PostAnswerView(APIView):
    serializer_class=PostQuestionSerializer
    def put(self,request):
        # post_question_serializer=PostQuestionSerializer(data=request.data)   
        authorization_header = request.headers.get('Authorization')
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired.')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing.')

        user = Profile.objects.filter(user_id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found.')
        
        try:
            post=Post.objects.get(id=request.data['post'],user=payload['user_id'])   
        except Post.DoesNotExist:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT)
        try:
            question=PostQuestion.objects.get(id=request.data['id'])  
            question.is_answered = request.data['is_answered']
            question.answer =request.data['answer'] 
            question.save()
            # post_question_serializer.save()
            return Response("answered succressfully",status=status.HTTP_200_OK)
        except PostQuestion.DoesNotExist:
            return Response("question doesn't exists",status=status.HTTP_204_NO_CONTENT)    




class PostQuestionView(APIView):
    serializer_class=PostQuestionSerializer
    permission_classes = [AllowAny]
    def post(self,request):
        post_question_serializer=PostQuestionSerializer(data=request.data)   
        try:
            user_data=Profile.objects.get(user_id=request.data['user'])
        except Profile.DoesNotExist:
            return Response("user doesn't exists",status=status.HTTP_204_NO_CONTENT)
        try:
            post=Post.objects.get(id=request.data['post'])   
        except Post.DoesNotExist:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT)
        if post_question_serializer.is_valid() :
            post_question_serializer.save()
            return Response(post_question_serializer.data,status=status.HTTP_201_CREATED)
        return Response(post_question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request):
        post_question_serializer=PostQuestionSerializer(request.data)   
        authorization_header = request.headers.get('Authorization')
        
        try:
            post=Post.objects.get(id=request.data['post_id'])   
        except Post.DoesNotExist:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONTENT)
        try:
            question=PostQuestion.objects.get(id=request.data['question_id'])   
        except PostQuestion.DoesNotExist:
            return Response("question doesn't exists",status=status.HTTP_204_NO_CONTENT)    

        if post_question_serializer.is_valid() :
                post_question_serializer.save()
                return Response("answered successfully",status=status.HTTP_201_CREATED)
        return Response(post_question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        try:
            post=Post.objects.get(id=request.GET['post_id'])   
        except Post.DoesNotExist:
            return Response("post doesn't exists",status=status.HTTP_204_NO_CONT9ENT)
        try:
            question=PostQuestion.objects.get(id=request.GET['question_id']).delete()
            return Response("Deleted successfully",status=status.HTTP_200_OK)
        except PostQuestion.DoesNotExist:
            return Response("question doesn't exists",status=status.HTTP_204_NO_CONTENT)  
            


class StartReservedPayment(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        # request.data is coming from frontend
        amount = request.data['amount']
        username = request.data['username']
        reserve_product = request.data['reserve_product']

        user = Profile.objects.filter(user_id=username).first()
        post = Post.objects.filter(id=reserve_product).first()

        if not user or not post:
            return Response("Something went wrong", status=status.HTTP_404_NOT_FOUND)
        
        # setup razorpay client
        client = razorpay.Client(auth=(os.environ.get("RAZORPAY_PUBLIC_KEY"), os.environ.get("RAZORPAY_SECRET_KEY")))
        # create razorpay order
        payment = client.order.create({"amount": int(amount)*100, 
                                    "currency": "INR", 
                                    "payment_capture": "1"})                   
        # we are saving an order with isReserved=False
        

        """order response will be 
        {'id': 17, 
        'order_date': '23 January 2021 03:28 PM', 
        'order_product': '**product name from frontend**', 
        'order_amount': '**product amount from frontend**', 
        'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
        'isPaid': False}"""

        data = {
            "payment": payment,
            # "order": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)


class HandleReservedPaymentSuccess(APIView):
    def post(self,request):
        res = request.data["response"]
        data = request.data["data"]
        """res will be:
        {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
        'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
        'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
        """

        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # res.keys() will give us list of keys in res
        for key in res.keys():
            if key == 'razorpay_order_id':
                ord_id = res[key]
            elif key == 'razorpay_payment_id':
                raz_pay_id = res[key]
            elif key == 'razorpay_signature':
                raz_signature = res[key]
                
        user = Profile.objects.get(user_id=data['username'])
        post = Post.objects.get(id=data['reserve_product'])

        if(user==None or post==None):
            return Response("Something went wrong")

        checkprev = Reserve.objects.filter(reserve_product=post,user=user)
        if checkprev:
            expire_date = checkprev[0].expire_date
            if expire_date < timezone.now():
                Reserve.objects.filter(reserve_product=post,user=user).delete()
            else :
                return Response("Already Reserved",status=status.HTTP_204_NO_CONTENT)    
        reserve = Reserve.objects.create(reserve_product=post,
                                    user=user,
                                    isReserved=True,
                                    reserve_amount=data['amount'], 
                                    reserve_payment_id=request.data["payment_id"])

        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }

        client = razorpay.Client(auth=(os.environ.get("RAZORPAY_PUBLIC_KEY"), os.environ.get("RAZORPAY_SECRET_KEY")))

        # checking if the transaction is valid or not if it is "valid" then check will return None
        check = client.utility.verify_payment_signature(data)

        if check is not None:
            return Response('Something went wrong',status=status.HTTP_400_BAD_REQUEST)

        # if payment is successful that means check is None then we will turn isPaid=True
        serializer = ReservedSerializer(reserve)

     

        return Response("Successfull payment",status=status.HTTP_200_OK)


class StartProductPayment(APIView):
    def post(self,request):
        # request.data is coming from frontend
        amount = request.data['amount']
        username = request.data['username']
        order_product = request.data['order_product']

        user = Profile.objects.filter(user_id=username).first()
        post = Post.objects.filter(id=order_product).first()
        
        reserve = Reserve.objects.filter(reserve_product=order_product, user=user).first()

        if reserve and reserve.expire_date > timezone.now():
            amount = int(amount) - 10
               
        if not user or not post:
            return Response("Something went wrong", status=status.HTTP_404_NOT_FOUND)
        # setup razorpay client
        client = razorpay.Client(auth=(os.environ.get("RAZORPAY_PUBLIC_KEY"), os.environ.get("RAZORPAY_SECRET_KEY")))

        # create razorpay order
        payment = client.order.create({"amount": int(amount)*100, 
                                    "currency": "INR", 
                                    "payment_capture": "1"})


        """order response will be 
        {'id': 17, 
        'order_date': '23 January 2021 03:28 PM', 
        'order_product': '**product name from frontend**', 
        'order_amount': '**product amount from frontend**', 
        'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
        'isPaid': False}"""

        data = {
            "payment": payment,
        }
        return Response(data,status=status.HTTP_200_OK)



class HandleProductPaymentSuccess(APIView):
    def post(self,request):
        res = request.data["response"]
        data = request.data["data"]
        """res will be:
        {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
        'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
        'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
        """

        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # res.keys() will give us list of keys in res
        for key in res.keys():
            if key == 'razorpay_order_id':
                ord_id = res[key]
            elif key == 'razorpay_payment_id':
                raz_pay_id = res[key]
            elif key == 'razorpay_signature':
                raz_signature = res[key]

        # get order by payment_id which we've created earlier with isPaid=False
        user = Profile.objects.get(user_id=data['username'])
        post = Post.objects.get(id=data['order_product'])

        if(user==None or post==None):
            return Response("Something went wrong")
        order = Order.objects.create(order_product=post,
                                    user=user,
                                    order_amount=data['amount'], 
                                    order_payment_id=request.data["payment_id"])
        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }
        
       

        client = razorpay.Client(auth=(os.environ.get("RAZORPAY_PUBLIC_KEY"), os.environ.get("RAZORPAY_SECRET_KEY")))

        # checking if the transaction is valid or not if it is "valid" then check will return None
        check = client.utility.verify_payment_signature(data)

        if check is not None:
            return Response('Something went wrong',status=status.HTTP_400_BAD_REQUEST)

        # if payment is successful that means check is None then we will turn isPaid=True
        serializer = OrderSerializer(order)


     

        return Response(serializer.data,status=status.HTTP_200_OK)














# Product_categories = {
#     'Electronics':['Laptops','Power Banks','Pen drives & Storage','Tablets','Computer & Accessories','Headphones & earphones','Speakers','Camera & accessories','Gaming accessories'],
#     'Mobile':['Mobile','Mobile Accessories'],
#     'Appliances':['Televisions','Kitches Appliances','Air conditioners','Refrigerators','Washing machine','Microwaves','Chimneys','Dishwashers','Cooler'],
#     "Men's Fashion":['Clothing','Footware','Watches','Bags','Wallets','Luggage','Sunglasses','Accessories'],
#     "Women's Fashion":['Clothing','Footware','Watches','Fashion & Jewellery','Hanbags & clutches','Sunglasses'],
#     "Home":['kitchen & appliances','Furniture','Home Decor','Indoor Lighting','Art & Crafts','Garden & Outdoors'],
#     "Sports & Fitness":['Cycle','Exercies & Fitness','Sports accessories'],
#     "Baby Products":["Clothing","Footware","School bags","Toys and Games"],
#     "Vehicles":['Two wheelers & accessories','Four wheelers & accessories','others'],
#     "Others":['Stationary Products','Arts & Handicrafts','Beauty'],
# } 