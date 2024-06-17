import os
import streamlit as st
from urllib.parse import urlencode
import streamlit.components.v1 as components

# Supabase 초기화
from supabase import create_client, Client, ClientOptions
import supabase as sp

# 로컬 테스트시,
# from dotenv import load_dotenv
# load_dotenv()
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_KEY")
# supabase: Client = create_client(supabase_url, supabase_key)
#배포
supabase = sp.create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# 스타일 설정
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] > .main {
            background: #2B242B !important;
            color: #FDFDFE !important;
        }
        h1,h2,h3 {
            color: #874FD4 !important;
        }
        label{
            color: #FDFDFE !important;
        }
        [data-testid="baseButton-secondary"]{
            background-color: #874FD4 !important;
        }
        [data-testid="baseButton-secondary"]:disabled{
            background-color: #FDFDFE !important;
        }
    </style>
    <script async src="https://tally.so/widgets/embed.js"></script>
    """, unsafe_allow_html=True)

# URL 파라미터 처리
query_params = st.query_params.to_dict()
contact = None
if 'contact' in query_params.keys():
    contact = query_params['contact']
user_name = None
if 'user_name' in query_params.keys():
    user_name = query_params['user_name']
uuid = None
if 'uuid' in query_params.keys():
    uuid = query_params['uuid']
survey_cat = None
if 'survey_cat' in query_params.keys():
    survey_cat = query_params['survey_cat']
survey_id = None
if 'survey_id' in query_params.keys():
    survey_id = query_params['survey_id']

if uuid:
    st.session_state['uuid'] = uuid
    user = supabase.table('users').select('*').eq('id', uuid).execute()
    if not user.data:
        st.error("잘못된 접근입니다.")
    else:
        st.success(f"{user.data[0]['display_name']}님 환영합니다!")
elif contact and user_name:
# 테스트
    # admin = sp.create_client(supabase_url, supabase_key, ClientOptions(auto_refresh_token=False, persist_session=False))
    # 배포
    admin = sp.create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"], ClientOptions(auto_refresh_token=False, persist_session=False))
    if len(contact) == 11 and contact[:3] == "010":
        phone = "82" + contact[1:]
    try:
        result = admin.auth.admin.create_user(
            {"phone": phone, "phone_confirm":True}
        )
        uuid = result.user.id
        supabase.table("users").insert({'id':result.user.id, 'phone_number':phone, 'display_name':user_name})
        st.success(f"{user_name}님 환영합니다!")
    except Exception:
        try:
            registed_user = supabase.table("users").select("id").eq("phone_number",phone).single().execute()
            uuid = registed_user.data["id"]
            st.success(f"{registed_user.data['display_name']}님 환영합니다!")
        except Exception:
            st.warning("잘못된 접근입니다.")
else:
    st.error("잘못된 접근입니다.")

categories = ['출근 및 업무환경 미리보기', '팀원 및 분위기 미리보기', '보상 및 성장가능성 미리보기', '생활권역 이동(해외/타지역) 미리보기']
category_eng = {'출근 및 업무환경 미리보기': 'place', '팀원 및 분위기 미리보기': 'team', '보상 및 성장가능성 미리보기': 'growth', '생활권역 이동(해외/타지역) 미리보기': 'location'}
category_kor = {v: k for k, v in category_eng.items()}

# 기본 상태 초기화
if 'responses' not in st.session_state:
    st.session_state['responses'] = {category: False for category in categories}
    for category in categories:
        answer = supabase.table('simul_survey').select('*').eq('user_id', uuid).eq('category', category_eng[category]).execute()
        if answer.data:
            st.session_state['responses'][category] = True

if 'selected_categories' not in st.session_state:
    st.session_state['selected_categories'] = []

if 'company_data' not in st.session_state:
    st.session_state['company_data'] = None

# 설문 결과 저장
if survey_id and survey_cat:
    st.session_state['survey_id'] = survey_id
    supabase.table('simul_survey').insert({'user_id': uuid, 'category': survey_cat, 'survey_id': survey_id}).execute()
    st.session_state['responses'][category_kor[survey_cat]] = True
    st.success("설문 결과가 저장되었습니다!")

# Tally 설문 링크
tally_links = {
    '출근 및 업무환경 미리보기': "https://tally.so/r/wQrOPA",
    '팀원 및 분위기 미리보기': "https://tally.so/r/w5kr9o",
    '보상 및 성장가능성 미리보기': "https://tally.so/r/wdAg0o",
    '생활권역 이동(해외/타지역) 미리보기': "https://tally.so/r/mR42o9"
}

# 시뮬레이션 영역 선택 및 설문 처리
def handle_selection(category):
    if not st.session_state['responses'][category]:
        tally_form_url = f"{tally_links[category]}?{urlencode({'uuid': st.session_state['uuid'], 'category': category_eng[category]})}"
        st.markdown(f'<iframe src="{tally_form_url}&alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1" loading="lazy" width="100%" height="500px" frameborder="0" marginheight="0" marginwidth="0" sandbox="allow-top-navigation allow-scripts allow-same-origin allow-popups allow-top-navigation-by-user-activation">Loading…</iframe>', unsafe_allow_html=True)

# 시뮬레이션 영역 네모 상자 생성
for category in categories:
    box_color = '#FFBABA' if not st.session_state['responses'][category] else {
        '출근 및 업무환경 미리보기': '#DFF2BF',
        '팀원 및 분위기 미리보기': '#B3E5FC',
        '보상 및 성장가능성 미리보기': '#FFECB3',
        '생활권역 이동(해외/타지역) 미리보기': '#FFCDD2'
    }[category]
    status = '미응답' if not st.session_state['responses'][category] else '응답 완료'

    st.markdown(
        f"""
        <div style="padding: 20px; margin: 10px; background-color: {box_color}; border-radius: 10px;">
            <h4>{category} - {status}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    if not st.session_state['responses'][category]:
        handle_selection(category)

# 안내 및 비활성화된 선택 버튼
st.markdown("""
    <div style="padding: 20px; margin: 10px; background-color: #F0F0F0; border-radius: 10px;">
        <h4>설문을 진행해야 시뮬레이션이 가능합니다.</h4>
        <p style="color:#874FD4">아래 모든 영역에 시뮬레이션이 진행됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

disabled_buttons = []

for category in categories:
    if not st.session_state['responses'][category]:
        disabled_buttons.append(category)
    else:
        st.button(f'[{category}]', key=f'disabled_button_{category}', disabled=False, on_click=lambda c=category: st.session_state['selected_categories'].append(c))

for category in disabled_buttons:
    st.button(f'{category} (설문 응답 필요)', key=f'disabled_button_{category}', disabled=True)

# 하나라도 응답한 설문이 있는지 확인
any_responses = any(st.session_state['responses'].values())

if any_responses:
    # 기업 정보 입력
    st.title('기업 정보 입력')
    st.write("필수 입력 항목은 *로 표시됩니다.")
    
    company_name = st.text_input('기업 이름*', key='company_name', help="기업명은 필수 입력 항목입니다.")
    job_posting = st.text_input('채용공고', key='job_posting', help="채용공고를 입력하면 아래 항목이 바활성화됩니다.")
    
    if not job_posting:
        team_name = st.text_input('소속 팀 및 본부명', key='team_name')
        position = st.text_input('담당 직무 (이직 예정 포지션)', key='position')
        rank = st.text_input('담당 직급 (팀장급, 리더급)', key='rank')
    else:
        team_name = st.text_input('소속 팀 및 본부명', key='team_name', disabled=True)
        position = st.text_input('담당 직무 (이직 예정 포지션)', key='position', disabled=True)
        rank = st.text_input('담당 직급 (팀장급, 리더급)', key='rank', disabled=True)

    st.markdown("### 해당 기업의 입사 예정 상태를 알려주세요.")
    status_options = ["이직준비 중(정보 탐색 중)👀", "스카웃 제안 확인 후 채용 절차 진행 중💁‍♀️", "채용 확정 후 연봉 협상 중🤝", "오퍼레터 수락 후 입사일자 확정✅"]
    status = st.selectbox("", status_options, key='status')
    
    if st.button('정보 조회'):
        companies = {
            '회사A': {'fit_score': 85, 'comments': '회사A는 당신과 잘 맞습니다.'},
            '회사B': {'fit_score': 70, 'comments': '회사B는 보통입니다.'},
            '회사C': {'fit_score': 90, 'comments': '회사C는 당신과 매우 잘 맞습니다.'}
        }
        if company_name in companies:
            st.session_state['company_data'] = companies[company_name]
        else:
            st.session_state['company_data'] = None
            st.error(f'{company_name}에 대한 정보를 찾을 수 없습니다. 24시간 내에 알림을 보내드리겠습니다.')
            supabase.table('sumul_request').insert({'user_id': uuid, 'company_name': company_name, 'jd':job_posting, 'team':team_name, 'position':position, 'rank':rank, 'status':status}).execute()

    if st.session_state['company_data']:
        if st.button('시뮬레이션 결과 확인'):
            company_data = st.session_state['company_data']
            st.write(f"적합도 점수: {company_data['fit_score']}")
            st.write(f"코멘트: {company_data['comments']}")

st.markdown("""
---
### 문의
기타 오류 및 문의 사항은 아래에 문의 부탁드립니다.
- [카카오톡 플러스친구](http://pf.kakao.com/_xjxkJbG/chat)
- [지원전에 홈페이지](https://jiwon.in10s.co)
""")