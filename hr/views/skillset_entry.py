from __future__ import print_function
import datetime

from pyramid.view import view_config
import transaction

from hr.models import DBSession
from hr.models.User import User
from hr.models.Review import Review
from hr.models.Account import Account
from hr.models.SkillsetEntry import SkillsetEntry
from hr.models.Skillset import Skillset


@view_config(route_name='skillset_entry_add', request_method='GET', renderer="json")
def skillset_entry_add(request):
    rating = request.matchdict.get('rating')
    skillset_id = request.matchdict.get('skillset_id')
    person_id = request.matchdict.get('person_id')
    review_id = request.matchdict.get('review_id')
    interval = request.matchdict.get('interval')

    is_midyear = False
    if interval == "midyear":
        is_midyear = True

    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()
    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()
    person = DBSession.query(User).filter_by(id=long(person_id)).first()
    review = DBSession.query(Review).filter_by(id=long(review_id)).first()
    skillset = DBSession.query(Skillset).filter_by(id=long(skillset_id)).first()

    if user.permissions.is_administrator or person.manager_id == user.id:
        if is_midyear and (
                datetime.datetime.now() > account.midyear_review_end_date or datetime.datetime.now() < account.midyear_review_start):
            return {'ok': 'False'}
        if is_midyear == False and (
                datetime.datetime.now() > account.annual_review_end_date or datetime.datetime.now() < account.annual_review_start):
            return {'ok': 'False'}

        skillset_entry = SkillsetEntry(review, is_midyear, skillset, rating)
        DBSession.add(skillset_entry)
        transaction.commit()

        return {"ok": "True"}

    return {'ok': 'False'}


@view_config(route_name='skillset_entry_update', request_method='GET', renderer="json")
def skillset_entry_update(request):
    print("skillset entry update")
    rating = request.matchdict.get('rating')
    skillset_entry_id = request.matchdict.get('skillset_entry_id')
    person_id = request.matchdict.get('person_id')

    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()
    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()
    person = DBSession.query(User).filter_by(id=long(person_id)).first()
    skillset_entry = DBSession.query(SkillsetEntry).filter_by(id=long(skillset_entry_id)).first()

    if user.permissions.is_administrator or person.manager_id == user.id:
        if skillset_entry.is_midyear and (
                datetime.datetime.now() > account.midyear_review_end_date or datetime.datetime.now() < account.midyear_review_start):
            return {'ok': 'False'}
        if skillset_entry.is_midyear == False and (
                datetime.datetime.now() > account.annual_review_end_date or datetime.datetime.now() < account.annual_review_start):
            return {'ok': 'False'}
        DBSession.query(SkillsetEntry).filter_by(id=skillset_entry_id).update({'ranking': rating})
        return {"ok": "True"}

    return {'ok': 'False'}
    
