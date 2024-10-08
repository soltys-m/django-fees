from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import Signal, receiver

# TODO: commerce
# from commerce.models import Cart, Order
# from commerce.signals import cart_updated
from fees.helpers import get_purchaser_model
from fees.models import Plan, Pricing
from pragmatic.signals import apm_custom_context, SignalsHelper

User = get_user_model()


order_started = Signal()
order_started.__doc__ = """
Sent after order was started (awaiting payment)
"""

order_completed = Signal()
order_completed.__doc__ = """
Sent after order was completed (payment accepted, account extended)
"""


user_language = Signal()
user_language.__doc__ = """Sent to receive information about language for user account"""

account_automatic_renewal = Signal()
account_automatic_renewal.__doc__ = """
Try to renew the account automatically.
Should renew the user's UserPlan by recurring payments. If this succeeds, the plan should be extended.
"""

account_expired = Signal()
account_expired.__doc__ = """
Sent on account expiration.
This signal is send regardless ``account_deactivated``
it only means that account has expired due to plan expire date limit.
"""

account_deactivated = Signal()
account_deactivated.__doc__ = """
Sent on account deactivation, account is not operational (it could be not expired, but does not meet quota limits).
"""

account_activated = Signal()
account_activated.__doc__ = """
Sent on account activation, account is now fully operational.
"""
purchaser_change_package = Signal()
purchaser_change_package.__doc__ = """
Sent on account when plan was changed after order completion
"""

# activate_purchaser_plan = Signal()
# activate_purchaser_plan.__doc__ = """
# This signal should be called when user has succesfully registered (e.g. he activated account via e-mail activation).
# If you are using django-registration there is no need to call this signal.
# """


@receiver(post_save, sender=get_purchaser_model())
def set_default_purchaser_plan(sender, instance, created, **kwargs):
    """
    Creates default plan for the new user but also extending an account for default grace period.
    """

    if created:
        Plan.create_for_purchaser(instance)


# TODO: check
# Hook to django-registration to initialize plan automatically after user has confirm account

# @receiver(activate_purchaser_plan)
# def initialize_plan_generic(sender, purchaser, **kwargs):
#     try:
#         purchaser.plan.initialize()
#     except Plan.DoesNotExist:
#         return


# @receiver(cart_updated, sender=Cart)
# @apm_custom_context('signals')
# def new_item_in_cart(sender, item, **kwargs):
#     # if new plan added into cart, delete all other items
#     if isinstance(item.product, Pricing):
#         item.cart.item_set.exclude(id=item.id).delete()


# @receiver(pre_save, sender=Order)
# @apm_custom_context('signals')
# def order_status_changed(sender, instance, **kwargs):
#     if instance.pk and SignalsHelper.attribute_changed(instance, ['status']) and instance.status == Order.STATUS_PAYMENT_RECEIVED:
#         if instance.has_item_of_type(Pricing):
#             purchased_pricings = instance.items_of_type(Pricing)
#
#             if purchased_pricings.count() > 1:
#                 raise ValueError(f'Order {instance.number} contains multiple subscription pricing plans!')
#
#             purchased_pricing = purchased_pricings.first()  # order should have single pricing plan only actually
#
#             purchaser = instance.user
#             pricing = purchased_pricing.product
#             plan = pricing.plan
#
#             try:
#                 # extend (and upgrade if necessary) plan
#                 purchaser.plan.extend(package, pricing)
#             except ObjectDoesNotExist:
#                 # create new plan
#                 Plan.create_for_user(instance.user, pricing)
