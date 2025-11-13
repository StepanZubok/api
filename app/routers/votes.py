from fastapi import APIRouter, HTTPException, status, Depends
from app import hash_verify, schemas, models, database
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, auth, database, models

router = APIRouter(prefix = "/votes", tags=["Votes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote : schemas.VoteBase, db : Session = Depends(database.get_db), current_user_id : int = Depends(auth.get_current_user_id)):
    
    post = db.query(models.PostsTable).filter(models.PostsTable.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user_id)
    found_vote = vote_query.first()
    
    if (vote.vote_option == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user_id)
        db.add(new_vote)
        db.commit()
        return {"msg" : "added vote"}
    else:
        if not found_vote: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"msg" : "deleted vote"}