from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage,default_storage
from django.core.mail import send_mail, EmailMessage
from core.models import Document,Userallowed,police
from core.forms import DocumentForm  
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate,login as auth_login
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction
from .paytm import generate_checksum, verify_checksum
import os 
import pyqrcode
import png 
import random 
import base64 
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
global doc
def adminlogin(request):
    if(request.method=="POST" and "admin_login" in request.POST):
        global w
        w=authenticate(username=request.POST.get("name"), password=request.POST.get("password"))
        print(w)
        if(w!=None):
            return render(request,"user_allowed.html",)
        else:
            return render(request,"adminlogin.html",)
    return render(request,"adminlogin.html",)
def home(request):
    documents= Document.objects.all()
    return render(request, 'home.html', { 'documents': documents })

"""def simple_upload(request): 
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile'] 
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile) 
        uploaded_file_url = fs.url(filename)  
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_path = os.path.join(BASE_DIR,'media')
        full_path=os.path.join(media_path,myfile.name) 
        qr=pyqrcode.create(uploaded_file_url)
        filename_before=filename.rsplit(".")
        filename1=filename_before[0]+".png"
        s=qr.png(filename1,scale=6) 
        '''from fpdf import FPDF 
        pdf=FPDF()
        pdf.add_page()
        pdf.image(filename1,x=50,y=None,w=60,h=60,type="",link=uploaded_file_url)'''
        return render(request, 'simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'simple_upload.html')"""


def model_form_upload(request): 
    id="" 
    msg=""
    form = DocumentForm() 
    if (request.method == 'POST' and user_count>0):
        form = DocumentForm(request.POST, request.FILES,request.POST)   
        if form.is_valid(): 
            form.save() 
            email=form.cleaned_data['Email']
            document_count=Document.objects.values_list('document').count() 
            document_last=Document.objects.values_list('document')[document_count-1] 
            document_name=document_last[0]
            print(email)
            t=Document.objects.last() 
            num_list=['0','1','2','3','4','5','6','7','8','9'] 
            password1="" 
            for i in range(0,8):
                password1=password1+random.choice(num_list)
            t.password=password1   
            print(type(document_name)) 
            document_name1=document_name.encode('ascii')
            document_encode=str(base64.b64encode(document_name1))
            ax=document_encode[2:-1]
            t.file_url=ax 
            print(ax)
            t.save()
            qr=pyqrcode.create(ax) 
            filename=document_name.rsplit(".") 
            filename1=filename[0].split("/")  
            filename2=filename1[1]+".png"
            qr.png(filename2,scale=6)   
            
            """mail=EmailMessage('QR',password1,'vmneelamegam2000@gmail.com',[email])
            #mail.attach(filename2,filename2.content_type)
            mail.send()"""
            subject = 'QRcode scanner for license'
            message = password1
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ] 
            mail=EmailMessage( subject, message, email_from, recipient_list )   
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            mail.attach_file(os.path.join(BASE_DIR,filename2))
            mail.send() 
            msg="Your successfully uploaded"
            return redirect('model_form_upload') 
    return render(request, 'model_form_upload.html', {'form': form,'msg':msg})  
def mypass(request):   
    m=""
    if(request.POST.get("pswd")==request.POST.get("pswd3")):
        user_data=Document.objects.filter(Email=request.POST.get("email"),password=request.POST.get("old_pswd")).update(password=request.POST.get("pswd")) 
    user_data1=Document.objects.filter(Email=request.POST.get("email"),password=request.POST.get("pswd"))
    """if(len_user_data==1):
        userdata.password=request.POST.get("pswd")
        return render(request,'mypass.html',{u:"you have change the password successfully"}) 
    else:"""   
    c=0
    if(user_data1):  
        subject = 'QRcode scanner for license'
        message = "Password has successfully changed"+" "+request.POST.get("pswd")
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get("email"), ] 
        mail=EmailMessage( subject, message, email_from, recipient_list )   
        mail.send()  
        c=1
        m="Your password is changed successfully" 
    elif(len(Document.objects.filter(Email=request.POST.get("email"),password=request.POST.get("old_pswd")))==0 and request.method=="POST"):
        m="Your entered email or password is incorrect"  
    else:
        m="" 
    print(m)
    return render(request,'mypass.html',{"m":m})
def user_req(request): 
    print(1)
    if("scanner" in request.POST and request.method=="POST" and pol_count>0 ):
        print(2)
        cap = cv2.VideoCapture(0+cv2.CAP_DSHOW) 
        font = cv2.FONT_HERSHEY_PLAIN
        decodedObjects=[]
        while decodedObjects==[]:
            _, frame = cap.read()
            decodedObjects = pyzbar.decode(frame)
            for obj in decodedObjects:
                points = obj.polygon
                (x,y,w,h) = obj.rect
                pts = np.array(points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                    (255, 0, 0), 3)
                id =obj.data.decode("utf-8")
            cv2.imshow("QR Reader", frame)
            key = cv2.waitKey(10) & 0xFF
            if decodedObjects!=[] :
                cv2.destroyAllWindows()  
        return render(request,"user_req.html",{"id":id})
    if('proceed' in request.POST and request.method=="POST" and pol_count>0):  
        print(3)
        userdata=Document.objects.filter(Q(file_url=request.POST.get("id1"))&Q(password=request.POST.get("password1")))
        print(userdata)
        return render(request,"user_req.html",{"userdata":userdata})
    return render(request,"user_req.html",) 
def userlogin(request):
    if(request.method=="POST"): 
        global user 
        global pol  
        global e1 
        global p1 
        global doc_count
        global user_count
        global pol_count
        e1=request.POST.get("email1")
        p1=request.POST.get("password1")
        print(request.POST.get("email1"),request.POST.get("password1"))
        doc=Document.objects.filter(Q(Email=request.POST.get('email1'))&Q(password=request.POST.get("password1")))
        user=Userallowed.objects.filter(Q(email=request.POST.get('email1'))&Q(password=request.POST.get('password1')))
        pol=police.objects.filter(Q(Email=request.POST.get('email1'))&Q(password=request.POST.get('password1')))
        doc_count=doc.count()
        user_count=user.count()
        pol_count=pol.count()
        if(doc.count()>0):
            print(1)
            return redirect('user')
        elif(user.count()>0):
            return redirect('model_form_upload')
        elif(pol.count()>0):
            print(2)
            return redirect('user_req') 
        else: 
            return render(request,"adminlogin.html",)
    return render(request,"adminlogin.html",)
def user(request):
    userdata=Document.objects.filter(Q(Email=e1)&Q(password=p1))
    print(userdata)
    if("logout" in request.POST):
        return redirect('adminlogin')
    return render(request,"user.html",{'userdata':userdata,'e1':e1})  
def forgetpass(request):   
    '''msg=""
    if(request.method=="POST"): 
        num_list=['0','1','2','3','4','5','6','7','8','9'] 
        password1="" 
        for i in range(0,8):
            password1=password1+random.choice(num_list) 
        user_data=Document.objects.filter(Email=request.POST.get("email")).update(password=password1)   
        subject = 'QRcode scanner for license Forget password'
        message = "Password has succesfully changed"+" "+password1
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get("email"), ] 
        mail=EmailMessage( subject, message, email_from, recipient_list )   
        mail.send()  
        if(user_data>0):
            msg="your password is changed succesfully and mail sent" 
        elif(user_data==0):
            msg="your email is incorrect or not found" 
    return render(request,"forget_pass.html",{"msg":msg}) '''
    msg=""
    print(1)
    if(request.method=="POST"):
        global email1
        global otp1
        if('verify' in request.POST):
            print(otp1,request.POST.get('otp'))
            if(otp1==request.POST.get('otp')):
                return render(request,"new_password.html",)
            else:
                return render(request,"verifyer.html",)
        elif("change" in request.POST):
            if(request.POST.get('password')!="" and request.POST.get("confirm_password")!="" ):
                Document.objects.filter(Email=email1).update(password=request.POST.get('password'))
                return redirect('adminlogin')
            else:
                return render(request,"new_password.html",)
        else:
            email1=request.POST.get('email')
            num_list1=['0','1','2','3','4','5','6','7','8','9']
            otp1=""
            for i in range(0,5):
                otp1=otp1+random.choice(num_list1)
            subject="Forget password"
            mail_from=settings.EMAIL_HOST_USER
            recipient=[email1,]
            messages="Your OTP is "+otp1
            mail=EmailMessage(subject,messages,mail_from,recipient)
            mail.send()
            return render(request,"verifyer.html",)
    return render(request,"forget_pass.html",)
def qrcode_miss(request):  
    msg="" 
    if(request.method=='POST' and Document.objects.filter(Email=request.POST.get('email'),password=request.POST.get('password1'))):
        user_data=Document.objects.values_list('document').filter(Email=request.POST.get('email'),password=request.POST.get('password1'))
        m=user_data[0][0] 
        p=m.split('/')  
        print(p)
        t=p[1] 
        print(t)
        subject = 'QRcode scanner for license'
        message = "resend"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get('email'),]
        mail=EmailMessage( subject, message, email_from, recipient_list )   
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
        k=os.path.join(BASE_DIR,t)  
        print(k)
        mail.attach_file(k)
        mail.send()  
        msg="your qrcode is sent to  your email" 
    elif(request.method=='POST'and Document.objects.values_list('document').filter(Email=request.POST.get('email'),password=request.POST.get('password1')).count()==0):
        msg="your email or password is incorrect" 
    return render(request,'qrcode_miss.html',{"msg":msg})
def user_allowed(request):
    msg=""
    if(request.method=="POST" and "Register" in request.POST and w!=None):
        u=Userallowed()
        u.name=request.POST.get("name")
        u.email=request.POST.get("email")      
        num_list=['0','1','2','3','4','5','6','7','8','9'] 
        password1="" 
        for i in range(0,8):
            password1=password1+random.choice(num_list)
        u.password=password1  
        u.save()
        subject = 'Password'
        message = "your User password is "+ password1
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get('email'),]
        mail=EmailMessage( subject, message, email_from, recipient_list ) 
        mail.send()
        msg="Registerd successfully"
        return render(request,"user_allowed.html",{'msg':msg})
    if(request.method=="POST" and "Police Register" in request.POST and w!=None):
        u=police()
        u.name=request.POST.get("name")
        u.Email=request.POST.get("email")      
        num_list=['0','1','2','3','4','5','6','7','8','9'] 
        password1="" 
        for i in range(0,8):
            password1=password1+random.choice(num_list)
        u.password=password1  
        u.save()
        subject = 'Password'
        message = "your User password is "+ password1
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get('email'),]
        mail=EmailMessage( subject, message, email_from, recipient_list ) 
        mail.send()
        msg="Registerd successfully"
        return render(request,"user_allowed.html",{'msg':msg})

    return render(request,"user_allowed.html",)
def initiate_payment(request):
    if request.method == "GET":
        return render(request, 'pay.html')
    try:
        username = request.POST['username']
        password = request.POST['password']
        amount = int(request.POST['amount'])
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is None:
            raise ValueError
        auth_login(request=request, user=user)
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY
    print(2)
    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('TXN_AMOUNT', str(transaction.made_by.email)),
        ('CUST_ID', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )
    print(3)
    paytm_params = dict(params)
    print(4)
    checksum = generate_checksum(paytm_params, merchant_key)
    print(checksum)
    
    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print(paytm_params)
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        paytm_checksum = ''
        print(request.body)
        print(request.POST)
        received_data = dict(request.POST)
        print(received_data)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            print("Checksum Matched")
            received_data['message'] = "Checksum Matched"
        else:
            print("Checksum Mismatched")
            received_data['message'] = "Checksum Mismatched"

        return render(request, 'callback.html', context=received_data)
    return render(request,'callback.html',)









        






