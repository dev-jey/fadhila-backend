import graphene
from graphql_extensions.auth.decorators import login_required
from messenger.apps.cards.models import Card
from messenger.apps.cards.objects import CardType
from .models import Feedback
from .objects import FeedbackType
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist


class Query(graphene.AbstractType):
    '''Defines a query for a card's feedback'''

    def __init__(self):
        pass

    all_feedback = graphene.List(FeedbackType, card=graphene.String())

    @login_required
    def resolve_all_feedback(self, info, **kwargs):
        '''Resolves all the feedback'''
        try:
            card = kwargs.get('card', None).strip()
            card_id = Card.objects.get(serial=card)
            feedback = Feedback.objects.filter(
                card=card_id.id).order_by('card')
            return feedback
        except ObjectDoesNotExist as e:
            print(e)
            raise GraphQLError("Card not found!")


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
