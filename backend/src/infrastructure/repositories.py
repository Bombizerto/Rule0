from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities import Event, FormatRuleset, Round, Pod, EventStatus, PlayerStatus, User
from infrastructure.models_orm import EventModel, FormatRulesetModel, RoundModel, PodModel, UserModel

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        return User(
            id=model.id,
            alias=model.alias,
            password=model.password,
            email=model.email,
            is_guest=model.is_guest,
            role=model.role
        )

    def get_by_alias(self, alias: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.alias == alias).first()
        if not model:
            return None
        return User(
            id=model.id,
            alias=model.alias,
            password=model.password,
            email=model.email,
            is_guest=model.is_guest,
            role=model.role
        )

    def save(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            alias=user.alias,
            password=user.password,
            email=user.email,
            is_guest=user.is_guest,
            role=user.role
        )
        self.session.merge(model)
        self.session.commit()
        return user

    def delete(self, user_id: str):
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()


class FormatRulesetRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, ruleset_id: str) -> Optional[FormatRuleset]:
        model = self.session.query(FormatRulesetModel).filter(FormatRulesetModel.id == ruleset_id).first()
        if not model:
            return None
        return FormatRuleset(
            id=model.id,
            name=model.name,
            win_points=model.win_points,
            draw_points=model.draw_points,
            kill_points=model.kill_points,
            allows_custom_achievements=model.allows_custom_achievements
        )

    def save(self, ruleset: FormatRuleset) -> FormatRuleset:
        model = FormatRulesetModel(
            id=ruleset.id,
            name=ruleset.name,
            win_points=ruleset.win_points,
            draw_points=ruleset.draw_points,
            kill_points=ruleset.kill_points,
            allows_custom_achievements=ruleset.allows_custom_achievements
        )
        self.session.merge(model)
        self.session.commit()
        return ruleset


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def _map_to_domain(self, model: EventModel) -> Event:
        # Convertimos player_status de dict[str, str] a dict[str, PlayerStatus]
        domain_player_status = {k: PlayerStatus(v) for k, v in model.player_status.items()}
        
        domain_rounds = []
        for r_model in model.rounds:
            domain_pods = []
            for p_model in r_model.pods:
                domain_pods.append(Pod(
                    id=p_model.id,
                    table_number=p_model.table_number,
                    players_ids=list(p_model.players_ids),
                    winner_id=p_model.winner_id,
                    is_draw=p_model.is_draw,
                    proposed_winner_id=p_model.proposed_winner_id,
                    proposed_is_draw=p_model.proposed_is_draw,
                    confirmations=dict(p_model.confirmations) if p_model.confirmations else {},
                    is_disputed=p_model.is_disputed
                ))
            domain_rounds.append(Round(
                id=r_model.id,
                event_id=r_model.event_id,
                round_number=r_model.round_number,
                pods=domain_pods,
                is_active=r_model.is_active,
                created_at=r_model.created_at
            ))
            
        return Event(
            id=model.id,
            title=model.title,
            organizer_id=model.organizer_id,
            ruleset_id=model.ruleset_id,
            join_code=model.join_code,
            players=list(model.players),
            status=EventStatus(model.status),
            created_at=model.created_at,
            round_number=model.round_number,
            rounds=domain_rounds,
            player_status=domain_player_status
        )

    def _map_to_orm(self, event: Event) -> EventModel:
        # Convertir player_status de dict[str, Enum] a dict[str, str] para JSON
        orm_player_status = {k: v.value for k, v in event.player_status.items()}
        
        orm_rounds = []
        for r_domain in event.rounds:
            orm_pods = []
            for p_domain in r_domain.pods:
                orm_pods.append(PodModel(
                    id=p_domain.id,
                    round_id=r_domain.id,
                    table_number=p_domain.table_number,
                    players_ids=list(p_domain.players_ids),
                    winner_id=p_domain.winner_id,
                    is_draw=p_domain.is_draw,
                    proposed_winner_id=p_domain.proposed_winner_id,
                    proposed_is_draw=p_domain.proposed_is_draw,
                    confirmations=dict(p_domain.confirmations),
                    is_disputed=p_domain.is_disputed
                ))
            orm_rounds.append(RoundModel(
                id=r_domain.id,
                event_id=r_domain.event_id,
                round_number=r_domain.round_number,
                is_active=r_domain.is_active,
                created_at=r_domain.created_at,
                pods=orm_pods
            ))

        return EventModel(
            id=event.id,
            title=event.title,
            organizer_id=event.organizer_id,
            ruleset_id=event.ruleset_id,
            join_code=event.join_code,
            players=list(event.players),
            status=event.status.value,
            created_at=event.created_at,
            round_number=event.round_number,
            player_status=orm_player_status,
            rounds=orm_rounds
        )

    def get_by_id(self, event_id: str) -> Optional[Event]:
        model = self.session.query(EventModel).filter(EventModel.id == event_id).first()
        if not model:
            return None
        return self._map_to_domain(model)

    def get_by_join_code(self, join_code: str) -> Optional[Event]:
        model = self.session.query(EventModel).filter(EventModel.join_code == join_code).first()
        if not model:
            return None
        return self._map_to_domain(model)

    def get_by_organizer(self, organizer_id: str) -> List[Event]:
        models = self.session.query(EventModel).filter(EventModel.organizer_id == organizer_id).all()
        return [self._map_to_domain(m) for m in models]

    def get_by_player(self, player_id: str) -> List[Event]:
        models = self.session.query(EventModel).all()
        events = [self._map_to_domain(m) for m in models]
        # Filtrar en memoria por simplicidad ya que los players son JSON array
        return [e for e in events if player_id in e.players]

    def delete(self, event_id: str):
        model = self.session.query(EventModel).filter(EventModel.id == event_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    def get_pod_by_id(self, pod_id: str) -> Optional[Event]:
        # Para encontrar a qué evento pertenece un pod, podemos hacer un join o buscar el pod y luego el evento
        pod_model = self.session.query(PodModel).filter(PodModel.id == pod_id).first()
        if not pod_model:
            return None
        # pod_model.round.event
        event_model = pod_model.round.event
        return self._map_to_domain(event_model)

    def save(self, event: Event) -> Event:
        model = self._map_to_orm(event)
        self.session.merge(model)
        self.session.commit()
        return event

    def list_all(self) -> List[Event]:
        models = self.session.query(EventModel).all()
        return [self._map_to_domain(m) for m in models]
