# from fastapi import APIRouter, HTTPException, status, Depends
# from .. import schemas, models, database
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from typing import List
# from .. import auth
# from typing import Optional

# router = APIRouter(prefix="/posts", tags=["Posts"])

# @router.get("", response_model=List[schemas.PostVoteResponse])
# def get_posts(
#     db: Session = Depends(database.get_db), 
#     current_user: models.UsersTable = Depends(auth.get_current_user_id),  # Renamed for clarity
#     limit: int = 10, 
#     skip: int = 0, 
#     search: Optional[str] = ""
# ):
#     # Query posts belonging to the authenticated user
#     results = (db.query(models.PostsTable, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.PostsTable.id == models.Vote.post_id, isouter=True).group_by(models.PostsTable.id).filter(models.PostsTable.account_id == current_user.id).filter(models.PostsTable.title.contains(search)).limit(limit).offset(skip).all())
#     return [{"post": post, "vote": vote} for post, vote in results]
 
# @router.get("/{id}", response_model=schemas.PostVoteResponse)
# def get_post_id(id : int, db : Session = Depends(database.get_db), current_user_id : int = Depends(auth.get_current_user_id)):
#     # post = db.query(models.PostsTable).filter(models.PostsTable.id == id).first()
#     post = db.query(models.PostsTable, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.PostsTable.id == models.Vote.post_id, isouter=True).group_by(models.PostsTable.id).filter(models.PostsTable.id == id).first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     # if post.account_id != current_user_id:
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
#     p, v = post
#     return {"post" : p, "vote" : v}

# @router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
# def create_post(post : schemas.PostCreate, db : Session = Depends(database.get_db), current_user_id : int = Depends(auth.get_current_user_id)):
#     new_post = models.PostsTable(account_id = current_user_id.id, **post.dict())
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)
#     return new_post 

# @router.delete("/{id}")
# def delete_post(id : int, db: Session = Depends(database.get_db), current_user_id : int = Depends(auth.get_current_user_id)):
#     post_query = db.query(models.PostsTable).filter(models.PostsTable.id == id)
#     delete_post = post_query.first()
#     if not delete_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     if delete_post.account_id != current_user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
#     post_query.delete()
#     db.commit()
#     return delete_post

# @router.put("/{id}", response_model=schemas.PostResponse)
# def update_post(id : int, post : schemas.PostUpdate, db : Session=Depends(database.get_db), current_user_id : int = Depends(auth.get_current_user_id)):
#     post_query = db.query(models.PostsTable).filter(models.PostsTable.id == id)
#     update_post = post_query.first()
#     if not update_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
#     if update_post.account_id != current_user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
#     post_query.update(post.dict(exclude_unset=True))
#     db.commit()
#     db.refresh(update_post)
#     return update_post


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app import models, schemas, database, auth

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=List[schemas.PostVoteResponse])
def get_posts(
    db: Session = Depends(database.get_db), 
    current_user: models.UsersTable = Depends(auth.get_current_user_id),
    limit: int = 10, 
    skip: int = 0, 
    search: Optional[str] = ""
):
    """Get all posts belonging to the authenticated user."""
    results = (
        db.query(models.PostsTable, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.PostsTable.id == models.Vote.post_id, isouter=True)
        .group_by(models.PostsTable.id)
        .filter(models.PostsTable.account_id == current_user.id)
        .filter(models.PostsTable.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return [{"post": post, "vote": vote} for post, vote in results]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostCreate)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsersTable = Depends(auth.get_current_user_id)
):
    """Create a new post."""
    new_post = models.PostsTable(
        title=post.title,
        text=post.text,
        account_id=current_user.id  # Use .id not the object
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostVoteResponse)
def get_post(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UsersTable = Depends(auth.get_current_user_id)
):
    """Get a specific post by ID."""
    result = (
        db.query(models.PostsTable, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.PostsTable.id == models.Vote.post_id, isouter=True)
        .group_by(models.PostsTable.id)
        .filter(models.PostsTable.id == id)
        .filter(models.PostsTable.account_id == current_user.id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post, vote = result
    return {"post": post, "vote": vote}

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_post(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UsersTable = Depends(auth.get_current_user_id)
):
    """Delete a post."""
    post_query = db.query(models.PostsTable).filter(models.PostsTable.id == id)
    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.account_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Post deleted successfully"}

@router.put("/{id}", response_model=schemas.PostUpdate)
def update_post(
    id: int,
    updated_post: schemas.PostUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.UsersTable = Depends(auth.get_current_user_id)
):
    """Update a post."""
    post_query = db.query(models.PostsTable).filter(models.PostsTable.id == id)
    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.account_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return post_query.first()