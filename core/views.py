from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage,default_storage
from django.core.mail import send_mail, EmailMessage
from core.models import Document
from core.forms import DocumentForm  
from django.contrib import messages
import os 
import pyqrcode
import png 
import random 
import base64 
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
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
    if request.method == 'POST':
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
            msg="your successfully uploaded"
            return redirect('model_form_upload')
    else:
        form = DocumentForm()  
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
        message = "Password has succesfully changed"+" "+request.POST.get("pswd")
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get("email"), ] 
        mail=EmailMessage( subject, message, email_from, recipient_list )   
        mail.send()  
        c=1
        m="your password is changed succesfully" 
    elif(len(Document.objects.filter(Email=request.POST.get("email"),password=request.POST.get("old_pswd")))==0 and request.method=="POST"):
        m="your email or password is incorrect"  
    else:
        m="" 
    print(m)
    return render(request,'mypass.html',{"m":m})
def user_req(request): 
    if("scanner" in request.POST and request.method=="POST"):
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
    if('proceed' in request.POST and request.method=="POST"):  
        userdata=Document.objects.filter(file_url=request.POST.get("id1")).filter(password=request.POST.get("password1"))
        return render(request,"user_req.html",{"userdata":userdata})
    return render(request,"user_req.html",) 
def user(request):
    return render(request,"user.html",)  
def forget_pass(request):   
    msg=""
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
    return render(request,"forget_pass.html",{"msg":msg}) 
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
        






