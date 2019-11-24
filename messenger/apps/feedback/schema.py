import graphene
from django.utils import timezone
from datetime import timedelta
from graphql_extensions.auth.decorators import login_required
from messenger.apps.cards.models import Card
from messenger.apps.cards.objects import CardType, TrackerType
from .models import Feedback
from messenger.apps.cards.models import Tracker
from .objects import FeedbackType
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist


class AllFeedback(graphene.ObjectType):
    tracking_details = graphene.Field(TrackerType)
    feedback = graphene.List(FeedbackType)

class Query(graphene.AbstractType):
    '''Defines a query for a card's feedback'''

    def __init__(self):
        pass

    all_feedback = graphene.Field(AllFeedback, card=graphene.String())

    @login_required
    def resolve_all_feedback(self, info, **kwargs):
        '''Resolves all the feedback'''
        try:
            card = kwargs.get('card', None).strip()
            card_id = Card.objects.get(serial=card)
        except ObjectDoesNotExist as e:
            print(e)
            raise GraphQLError("Card not found!")
        if not card_id.owner:
            return GraphQLError("This card is valid but not registered by the owner to our system yet")
        tracking_details = None
        if card_id.owner != info.context.user:
            try:
                tracking_details = Tracker.objects.get(serial=card_id.serial, tracker=info.context.user.id)
            except Exception as e:
                print(e)
                return GraphQLError('You are not tracking this card yet')
            
            tracking_count = Tracker.objects.filter(serial=card_id.serial).filter(tracker=info.context.user.id).filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                )
            if not tracking_count:
                return GraphQLError('You have used the maximum time allocated for tracking this card: 7 days')
        feedback = Feedback.objects.filter(
            card=card_id.id).order_by('card')
        return AllFeedback(feedback=feedback, tracking_details=tracking_details)


class AddFeedback(graphene.Mutation):
    '''Add card feedback'''
    # Returns the card instance info
    feedback = graphene.Field(FeedbackType)

    class Arguments:
        '''Takes in card details as arguments'''
        card = graphene.String()
        message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        '''Add feedback mutation'''
        try:
            card = Card.objects.get(serial=kwargs.get('card', None).strip())
            if card.owner == info.context.user:
                return GraphQLError("You cannot give feedback on your own card")
            feed = Feedback.objects.filter(
                giver=info.context.user.id
            ).filter(card__serial=card.serial).count()
            if feed >= 3:
                return GraphQLError("Sorry. You can only give 3 feedback messages per card.")
            feedback = Feedback(
                card=card,
                giver=info.context.user,
                message=kwargs.get('message', None).strip()
            )
            feedback.save()
            return AddFeedback(feedback=feedback)
        except ObjectDoesNotExist as e:
            print(e)
            raise GraphQLError('The card was not found')


class Mutation(graphene.ObjectType):
    '''All the mutations for this schema are registered here'''
    add_feedback = AddFeedback.Field()
