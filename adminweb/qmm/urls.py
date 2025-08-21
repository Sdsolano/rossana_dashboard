from django.urls import path,include

from .views import *



urlpatterns = [
    path('',LandingView.as_view(),name='qmm-landing'),
    path('neworder/',NewOrderMeetView.as_view(),name='qmm-neworder-meet'),
    path('order/',OrderMeetView.as_view(),name='qmm-order-meet'),
    path('order/step2/<day>/',OrderMeetStep2View.as_view(),name='qmm-order-step2'),
    path('order/step3/<day>/<meet>/',OrderMeetStep3View.as_view(),name='qmm-order-step3'),
    path('checkout/<day>/<meet>/',CheckoutView.as_view(),name='qmm-checkout'),
    path('pay_verify/<meet>/',PayView.as_view(),name='qmm-verify-and-pay'),
    path('pay/checkout/<pay_id>/',PayCheckoutStripeView.as_view(),name='qmm-pay-checkout-stripe'),
    path('pay/confirm/<pay>/',PayConfirmView.as_view(),name='qmm-pay-confirm'),
    path('pay/cancel/<pay>/',PayCancelView.as_view(),name='qmm-pay-cancel'),
    path('cancel/<meet>/',MeetCancelView.as_view(),name='qmm-meet-cancel'),
    path('cancelth/<meet>/',MeetCancelTherapistView.as_view(),name='qmm-meet-cancel-th'),
    path('redate/<meet>/',MeetRedateView.as_view(),name='qmm-meet-redate'),
    path('login/',LoginView.as_view(),name='qmm-login'),
    path('logout/',LogoutView.as_view(),name='qmm-logout'),
    path('therapist/',TherapistView.as_view(),name='qmm-therapist'),
    path('therapist/lockday/<day>/',TherapistLockDayView.as_view(),name='qmm-therapist-lock-day'),
    path('therapist/unlockday/<day>/',TherapistUnlockDayView.as_view(),name='qmm-therapist-unlock-day'),
    path('therapist/availability/',TherapistAvailabilityView.as_view(),name='qmm-therapist-availability')
    #path('checkout/',CheckoutView.as_view(),name="shop-checkout-confirm")

]