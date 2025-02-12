from operator import truediv

import groq
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_200_OK

from .models import *
from .forms import *
from .utils import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.utils import timezone
import json
from django.contrib import messages



def getpostings(request):
    jobs = postings.objects.all().order_by('-id')
    # Pass 'jobs' instead of 'jo' to be more descriptive
    return render(request, 'organization/postings.html', {'jobs': jobs})
def register(request):
    if request.method == 'POST':
        # Extract data from the POST request
        org_name = request.POST.get('orgname')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        address = request.POST.get('address')
        description = request.POST.get('description')

        # Validate required fields
        if not all([org_name, email, password, address, description]):
            return render(request, 'users/register.html', {
                'error': 'All fields are required.'
            })

        # Check if the user already exists in the User table
        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {
                'error': 'A user with this email already exists.'
            })

        # Check if the organization already exists in the organization table
        if organization.objects.filter(orgname=org_name).exists():
            return render(request, 'users/register.html', {
                'error': 'An organization with this name already exists.'
            })

        # Store user data in the session for later use
        user_data = {
            'username': org_name,
            'email': email,
            'password': password,
            'address': address,
            'description': description,
        }
        request.session['pending_user'] = user_data

        # Generate and store a verification code
        code = generate_verification_code()
        request.session['verification_code'] = code
        request.session['code_generated_at'] = now().timestamp()

        # Send verification email
        send_verification_email(email, code)

        # Redirect to the email verification page
        return redirect('verify_email')

    # Render the registration form for GET requests
    return render(request, 'users/register.html')

def verify_email(request):
    # Check if we have pending registration
    pending_user = request.session.get('pending_user')
    if not pending_user:
        return redirect('reg')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submitted_code = data.get('verification_code')
            stored_code = request.session.get('verification_code')
            code_generated_at = request.session.get('code_generated_at')

            current_time = timezone.now().timestamp()
            is_expired = (current_time - code_generated_at) > 30

            if stored_code and submitted_code == stored_code and not is_expired:
                # Create the user
                user = User.objects.create_user(
                    username=pending_user['username'],
                    email=pending_user['email'],
                    password=pending_user['password']
                )

                # Clean up session
                for key in ['pending_user', 'verification_code', 'code_generated_at']:
                    if key in request.session:
                        del request.session[key]

                # Authenticate and login the user
                authenticated_user = authenticate(
                    request,
                    username=pending_user['username'],
                    password=pending_user['password']
                )

                if authenticated_user is not None:
                    login(request, authenticated_user, backend='django.contrib.auth.backends.ModelBackend')
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Authentication failed'})
            else:
                error = 'Code expired' if is_expired else 'Invalid code'
                return JsonResponse({'success': False, 'error': error})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'users/verify_email.html')

def resend_code(request):
    if request.method == 'POST':
        pending_user = request.session.get('pending_user')
        if not pending_user:
            return JsonResponse({'success': False, 'error': 'No pending registration'})

        try:
            # Generate new code
            code = generate_verification_code()
            del request.session['verification_code']
            del request.session['code_generated_at']
            request.session['verification_code'] = code
            request.session['code_generated_at'] = timezone.now().timestamp()
            send_verification_email(pending_user['email'], code)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def login_view(request):
    if request.method == 'POST':
        # Extract data from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate required fields
        if not all([username, password]):
            return render(request, 'users/login.html', {
                'error': 'Both username and password are required.'
            })

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the user belongs to an organization
            try:
                org = organization.objects.get(org=user)
                # Log the user in
                login(request, user)
                # Store organization details in the session (optional)
                request.session['org_id'] = org.id
                request.session['org_name'] = org.orgname
                return redirect('home')  # Redirect to the home page or dashboard
            except organization.DoesNotExist:
                return render(request, 'users/login.html', {
                    'error': 'This user is not associated with any organization.'
                })
        else:
            # Invalid credentials
            return render(request, 'users/login.html', {
                'error': 'Invalid username or password.'
            })

    # Render the login form for GET requests
    return render(request, 'users/login.html')

def logoutView(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            email = User.objects.get(username=username).email
            reset_code = generate_verification_code()
            request.session['reset_code'] = reset_code
            request.session['reset_email'] = email
            request.session['username'] = username
            request.session['code_generated_at'] = timezone.now().timestamp()

            # Send reset code email
            send_reset_code_email(email, reset_code)

            return redirect('verify_reset_code')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this username.')

    return render(request, 'users/forgot_password.html')


def verify_reset_code(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('forgot_password')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submitted_code = data.get('verification_code')
            stored_code = request.session.get('reset_code')
            code_generated_at = request.session.get('code_generated_at')

            # Check if code is expired (30 seconds)
            current_time = timezone.now().timestamp()
            is_expired = (current_time - code_generated_at) > 30

            if stored_code and submitted_code == stored_code and not is_expired:
                request.session['reset_verified'] = True
                return JsonResponse({'success': True})
            else:
                error = 'Code expired' if is_expired else 'Invalid code'
                return JsonResponse({'success': False, 'error': error})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request'})

    return render(request, 'users/verify_reset_code.html')


def resend_reset_code(request):
    if request.method == 'POST':
        reset_email = request.session.get('reset_email')
        if not reset_email:
            return JsonResponse({'success': False, 'error': 'No pending reset request'})

        try:
            # Generate new code
            reset_code = send_reset_code_email()
            request.session['reset_code'] = reset_code
            request.session['code_generated_at'] = timezone.now().timestamp()

            # Send new code
            send_reset_code_email(reset_email, reset_code)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def reset_password(request):
    if not request.session.get('reset_verified'):
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/reset_password.html')

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/reset_password.html')

        try:
            user = User.objects.get(username=request.session['username'])
            user.set_password(password1)
            user.save()

            # Clean up session
            for key in ['reset_email', 'reset_code', 'code_generated_at', 'reset_verified']:
                if key in request.session:
                    del request.session[key]

            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'An error occurred. Please try again.')

    return render(request, 'users/reset_password.html')
@login_required()
def create_posting(request):

    user_org = organization.objects.get(org=request.user)  # Get the user's organization


    if request.method == 'POST':
        form = postingsForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)  # Don't save immediately
            interview.org = user_org  # Assign the organization
            interview.save()
            messages.success(request, 'Custom interview created successfully!')
            return redirect('custom_interview_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = postingsForm()

    return render(request, 'organization/createjobposting.html', {'form': form})
def create_custom_interview(request):
    user_org = organization.objects.get(org=request.user)  # Get the user's organization

    if request.method == 'POST':
        form = CustomInterviewsform(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)  # Don't save immediately
            interview.org = user_org  # Assign the organization
            interview.save()
            messages.success(request, 'Custom interview created successfully!')
            return redirect('custom_interview_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomInterviewsform()

    return render(request, 'organization/createcustominterview.html', {'form': form})
@login_required()
def Attempted(request):
    Id = request.data.get('id')
    if Application.objects.filter(id=Id) is None:
        return Response({'error' : 'invalid Application id'},status=HTTP_400_BAD_REQUEST)
    if request.user != Application.objects.filter(id=Id).first().user:
        return Response({'error' : 'unauthorized'},status=HTTP_401_UNAUTHORIZED)
    obj = Application.objects.filter(id=Id).first()
    obj.attempted = True
    return Response(HTTP_200_OK)
def Cheated(request):
    Id = request.data.get('id')
    if Application.objects.filter(id=Id) is None:
        return Response({'error' : 'invalid Application id'},status=HTTP_400_BAD_REQUEST)
    if request.user != Application.objects.filter(id=Id).first().user:
        return Response({'error' : 'unauthorized'},status=HTTP_401_UNAUTHORIZED)
    obj = Application.objects.filter(id=Id).first()
    obj.isCheated = True
    obj.save()
    return Response(HTTP_200_OK)
@login_required(login_url='reg/')
def Apply(request):
    Id = request.data.get('id')
    if Custominterviews.objects.filter(id=Id) is None:
        return Response({'error': 'invalid Application id'}, status=HTTP_400_BAD_REQUEST)
    obj = Application.objects.create(user=request.user,interview=Custominterviews.objects.get(id=Id))
    obj.save()
    return
@login_required
def chatcreate(request, applicationid):
    if Application.objects.get(id=applicationid).first() is None:
        messages.error(request,"Application Not found")
        return redirect('home')
    convo = Customconversation.objects.create(Application=Application.objects.get(id=applicationid).first())
    return redirect('compchat', convoid=convo.id)
@login_required
@csrf_exempt
def chat(request, convoid):
    convo = get_object_or_404(Customconversation, id=convoid)

    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        user_response = data.get('response')
        if user_response:
            Customquestions.objects.create(convo=convo, question=user_response, user='user')
            questions_list = list(Customquestions.objects.filter(convo=convo).values_list('question', flat=True))

            ques = ques = convo.Application.interview.questions
            post_title = convo.Application.interview.post
            reply, next_question = llm(questions_list, convoid, user_response, post_title,ques)

            if reply:
                Customquestions.objects.create(convo=convo, question=reply, user='ai')
            if next_question:
                Customquestions.objects.create(convo=convo, question=next_question, user='ai')

            if "INTERVIEW_COMPLETE" in next_question:
                convo.Application.attempted = True
                convo.Application.completed = True
                convo.Application.save()
                messages.success(request,"You have successfully finished the interview")
                return redirect('home')

            return JsonResponse({
                "reply": reply,
                "next_question": next_question,
            })

        return JsonResponse({"error": "Invalid response"}, status=400)

    # Fetch all questions for this conversation
    questions_list = Customquestions.objects.filter(convo=convo)

    # Initialize with a default question if no questions exist
    if not questions_list.exists():
        first_question = "Welcome to the interview! Can you tell me about your experience in this field?"
        Customquestions.objects.create(convo=convo, question=first_question, user='ai')
        questions_list = Customquestions.objects.filter(convo=convo)

    return render(request, 'bot/chat.html', {
        'convo': convo,
        'questions': questions_list,
    })
    # Fetch all questions for this conversation
    questions_list = Customquestions.objects.filter(convo=convo)

    # Initialize with a default question if no questions exist
    if not questions_list.exists():
        first_question = "Welcome to the interview! Can you tell me about your experience in this field?"
        questions.objects.create(convo=convo, question=first_question, user='ai')
        questions_list = questions.objects.filter(convo=convo)

    return render(request, 'bot/chat.html', {
        'convo': convo,
        'questions': questions_list,
    })


@login_required
def evaluate_interview(request, application_id):
    groq_client = groq.Groq(api_key="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")
    application = get_object_or_404(Application, id=application_id)

    # Check if interview is already evaluated
    if leaderBoard.objects.filter(Application=application).exists():
        messages.warning(request, 'This interview has already been evaluated.')
        return redirect('home')  # Replace 'home' with your home URL name
    if application.isCheated:
        messages.warning(request, 'This interview has recorded malpractice.')
        return redirect('home')
    if not application.attempted:
        messages.warning(request, 'This interview has not been attempted.')
        return redirect('home')
    conversation = get_object_or_404(Customconversation, Application=application)
    interview = application.interview
    qa_pairs = Customquestions.objects.filter(convo=conversation).order_by('created_at')

    if not qa_pairs.exists():
        messages.error(request, 'No conversation found for evaluation.')
        return redirect('home')  # Replace 'home' with your home URL name

    # Extract questions and answers
    questions = []
    answers = []
    timestamps = []

    for i in range(0, len(qa_pairs), 2):  # Assuming alternating question-answer pairs
        if i + 1 < len(qa_pairs):  # Make sure we have both Q and A
            questions.append(qa_pairs[i].question)
            answers.append(qa_pairs[i + 1].question)  # Answer stored in question field
            timestamps.append((qa_pairs[i + 1].created_at - qa_pairs[i].created_at).total_seconds())

    try:
        # Initialize scores
        technical_scores = []

        # Evaluate each Q&A pair
        for q, a in zip(questions, answers):
            technical_score = evaluate_answer_quality(
                groq_client,
                q, a,
                f"Job Post: {interview.post}\nExperience Required: {interview.experience}\nDescription: {interview.desc}"
            )
            technical_scores.append(technical_score)

        # Evaluate corporate fit
        corporate_fit_score = evaluate_corporate_fit(
            groq_client,
            json.dumps(list(zip(questions, answers))),
            interview.desc
        )
        is_cheated = check_cheating(groq_client, json.dumps(list(zip(questions, answers))))
        technical_weight = 0.6  # 60% weight for technical evaluation
        corporate_fit_weight = 0.4  # 40% weight for corporate fit

        final_score = (
                (sum(technical_scores) / len(technical_scores) * technical_weight) +
                (corporate_fit_score * corporate_fit_weight)
        ) if technical_scores else 0

        application.attempted = True
        application.completed = True
        application.isCheated = is_cheated
        application.save()

        # Create leaderboard entry
        leaderBoard.objects.create(
            Application=application,
            Score=round(final_score, 2)
        )

        messages.success(request, 'Interview evaluation completed successfully.')

    except Exception as e:
        messages.error(request, f'Error during evaluation: {str(e)}')
        application.attempted = True
        application.completed = False
        application.save()
    return redirect('home')
