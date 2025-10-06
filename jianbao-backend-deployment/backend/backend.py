from fastapi import FastAPI, HTTPException, Depends, Security, Query
from sqlmodel import SQLModel, Session, create_engine, select, and_, true
from typing import Optional , List
from datetime import datetime, timedelta, timezone
from models import User, LoginRequest, LoginResponse, BatchDetailRequest, Appraisal, UserInfo, \
                    BatchDetailResponse , AppraisalResource, AppraisalResult, AppraisalUpdateItem, OrderUpdateResult, \
                    OrderUpdateResponse, AppraisalResultBatchRequest, BatchAddResultResponse, BatchAddResultData, FailedItem
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import jwt
from jose import JWTError
import json
from sqlalchemy import func



# ------------------ 数据库配置 ------------------
MYSQL_USER = "kaimen"
MYSQL_PASSWORD = "7xK9#mQp2$vL8"
MYSQL_HOST = "sh-cynosdbmysql-grp-1cwincl8.sql.tencentcdb.com"
MYSQL_PORT = 28288
MYSQL_DB = "lowcode-3gkr3shu8224cfca"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL, echo=True)



# ------------------ JWT 配置 ------------------
SECRET_KEY = "your_secret_key_here"   # 建议使用安全生成的随机字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 7200    # 2小时

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ------------------ FastAPI 应用 ------------------
app = FastAPI(title="Appraisal Management Platform", version="1.0")



# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://admin.kaimen.site"],
    allow_origin_regex=r"https://.*\.jianbao\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ------------------ 初始化数据库 ------------------
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ------------------ 依赖注入 ------------------
def get_session():
    with Session(engine) as session:
        yield session


# ------------------ 生成 JWT Token ------------------
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ------------------ 登录接口 ------------------
@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    # 查询用户
    statement = select(User).where(User.name == request.username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    # 简单密码校验（生产环境请使用加盐哈希）
    if user.password != request.password:
        raise HTTPException(status_code=401, detail="密码错误")

    # 生成 Token
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "accessToken": access_token,
            "expiresIn": ACCESS_TOKEN_EXPIRE_SECONDS
        }
    }

# ------------------ 从 token 中获取当前用户 ------------------
def get_current_user(token: str = Security(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的Token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token验证失败")

    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

# ------------------ 获取用户信息接口 ------------------
@app.get("/api/user/info")
def get_user_info(current_user: User = Depends(get_current_user)):
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "user_id": str(current_user.id),
            "username": current_user.name,
            "nickname": current_user.nickname or "",
            "phone": current_user.phone or "",
            "email": current_user.email or "",
            "avatar": current_user.avatar or "",
            "role": current_user.role or "user",
            "create_time": current_user.create_time.isoformat(),
            "update_time": current_user.update_time.isoformat(),
        },
    }


@app.get("/api/appraisal/list")
def get_appraisal_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1),
    appraisalId: Optional[str] = None,
    title: Optional[str] = None,
    firstClass: Optional[str] = None,
    appraisal_status: Optional[str] = None,
    createTime: Optional[str] = None,
    session: Session = Depends(get_session),
):
    filters = []

    if appraisalId:
        filters.append(Appraisal.id == appraisalId)
    if title:
        filters.append(Appraisal.title.contains(title))
    if firstClass:
        filters.append(Appraisal.first_class == firstClass)
    if appraisal_status:
        filters.append(Appraisal.appraisal_status == appraisal_status)

    # 时间解析函数
    def parse_time(ts: Optional[str]) -> Optional[int]:
        try:
            return int(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp())
        except Exception:
            return None

    if createTime and (t := parse_time(createTime)):
        filters.append(Appraisal.appraisal_create_time >= t)

    if not filters:
        filters.append(true())
    # 查询总数
    total = session.exec(
        select(func.count()).select_from(Appraisal).where(and_(*filters))
    ).one()

    # 分页查询
    stmt = (
        select(Appraisal)
        .where(and_(*filters))
        .order_by(Appraisal.appraisal_create_time.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
    )
    appraisals = session.exec(stmt).all()

    result_list = []

    for a in appraisals:
        # 查询 appraisal_resource
        res_stmt = select(AppraisalResource).where(AppraisalResource.appraisal_id == a.id)
        resources = session.exec(res_stmt).all()

        images, videos = [], []
        for r in resources:
            if not r.url:
                continue
            if r.url.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(r.url)
            elif r.url.lower().endswith((".mp4", ".mov", ".avi")):
                videos.append(r.url)

        result_list.append({
            "appraisal_id": a.id,
            "title": a.title or "",
            "description": a.desc or "",
            "appraisal_status": a.appraisal_status or "",
            "first_class": a.first_class or "",
            "images": images,
            "videos": videos,
            "create_time": a.appraisal_create_time,
        })

    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "total": total,
            "page": page,
            "page_size": pageSize,
            "total_pages": (total + pageSize - 1) // pageSize,
            "list": result_list,
        },
    }


@app.post("/api/appraisal/detail", response_model=BatchDetailResponse)
def get_batch_appraisal_detail(
    req: BatchDetailRequest,
    session: Session = Depends(get_session),
):
    if not req.ids:
        raise HTTPException(status_code=400, detail="ids 不能为空")

    # 查询订单
    orders_stmt = select(Appraisal).where(Appraisal.id.in_(req.ids))
    orders = session.exec(orders_stmt).all()

    if not orders:
        return BatchDetailResponse(code=200, message="未查询到结果", data=[])

    response_data = []
    for o in orders:
        # 查询该订单最新的鉴定结果
        latest_appraisal_stmt = (
            select(AppraisalResult)
            .where(AppraisalResult.order_id == o.id)
            .order_by(AppraisalResult.created_at.desc())
            .limit(1)
        )
        latest_appraisal_result = session.exec(latest_appraisal_stmt).first()

        appraisal_data = {}
        if latest_appraisal_result:
            appraisal_data = {
                "id": str(latest_appraisal_result.id),
                "user_id": str(latest_appraisal_result.user_id),
                "create_time": latest_appraisal_result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "update_time": latest_appraisal_result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "appraisal_status": 1,  # 可根据业务调整
                "appraisal_result": latest_appraisal_result.result,
                "notes": latest_appraisal_result.notes or "",
                "result": latest_appraisal_result.result,
                "reasons": [],          # 如果有存疑/驳回原因字段，可填充
                "custom_reason": ""     # 如果有自定义原因字段，可填充
            }
        
        # 🔹 查询用户手机号
        user_phone = None
        if o.userinfo_id:
            phone_stmt = (
                select(UserInfo.phone)
                .where(UserInfo.id == o.userinfo_id)
                .limit(1)
            )
            user_phone = session.exec(phone_stmt).first()

        response_data.append({
            "order_id": str(o.id),
            "title": o.title or "",
            "user_phone":  user_phone,
            "description": o.desc or "",
            "appraisal_class": o.first_class or "",
            "create_time": datetime.fromtimestamp(o.appraisal_create_time / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if o.appraisal_create_time else "",
            # "update_time": o.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "latest_appraisal": appraisal_data
        })

    return BatchDetailResponse(code=200, message="查询成功", data=response_data)


# ---------- 批量更新订单类目和状态接口 ----------
@app.post("/api/order/update", response_model=OrderUpdateResponse)
def update_appraisal_info(
    updates: List[AppraisalUpdateItem],
    session: Session = Depends(get_session),
):
    if not updates:
        raise HTTPException(status_code=400, detail="更新数据不能为空")

    results = []

    for item in updates:
        order = session.get(Appraisal, item.id)
        if not order:
            results.append(OrderUpdateResult(
                order_id=item.id,
                success=False,
                message="未找到该订单"
            ))
            continue

        try:
            if item.appraisal_class is not None and item.appraisal_class.strip() != "":
                order.first_class = item.appraisal_class
            if item.appraisal_status is not None:
                order.appraisal_status = item.appraisal_status

            session.add(order)
            results.append(OrderUpdateResult(
                order_id=item.id,
                success=True,
                message="更新成功"
            ))
        except Exception as e:
            results.append(OrderUpdateResult(
                order_id=item.id,
                success=False,
                message=f"更新失败: {str(e)}"
            ))

    session.commit()

    return OrderUpdateResponse(
        code=200,
        message="批量更新完成",
        data=results
    )


# -------------批量添加鉴定结果接口-------------

@app.post("/api/appraisal/result/add", response_model=BatchAddResultResponse)
def add_appraisal_results(
    req: AppraisalResultBatchRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not req.items:
        raise HTTPException(status_code=400, detail="items 不能为空")

    success_count = 0
    failed_items: List[FailedItem] = []

    for item in req.items:
        order = session.get(Appraisal, item.orderid)
        if not order:
            failed_items.append(FailedItem(order_id=item.orderid, reason="未找到对应订单"))
            continue

        try:
            # 生成备注内容
            notes = item.comment or ""
            if item.reasons:
                notes += f" | 原因: {', '.join(item.reasons)}"
            if item.customReason:
                notes += f" | 其他: {item.customReason}"

            # 插入新鉴定结果
            new_result = AppraisalResult(
                order_id=item.orderid,
                result=str(item.appraisalResult or "未知"),
                notes=notes,
                user_id=current_user.id,
            )
            session.add(new_result)
            success_count += 1

        except Exception as e:
            session.rollback()  
            failed_items.append(FailedItem(order_id=item.orderid, reason=f"插入失败: {str(e)}"))

    session.commit()

    return BatchAddResultResponse(
        code=200,
        message="批量修改完成",
        data=BatchAddResultData(
            success_count=success_count,
            failed_count=len(failed_items),
            failed_items=failed_items
        )
    )


# ------------------ 启动说明 ------------------
"""
运行方法：
1. 安装依赖： pip install fastapi uvicorn sqlmodel pymysql
2. 启动 MySQL 并创建数据库： CREATE DATABASE appraisal_db;
3. 运行服务： uvicorn fastapi_app_main:app --reload
4. 打开 Swagger UI: http://127.0.0.1:8000/docs
"""

