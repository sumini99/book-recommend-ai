# -------------------------------
# 🏗️ 책 시각화 (계단식 + 위로 쌓임)
# -------------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))  # 최근 책이 위로

    fig_height = max(5, len(books) * 1.4)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 2 + 1)
    ax.invert_yaxis()

    y = 1
    offset_direction = 1

    for idx, book in enumerate(books):
        color = book["color"]
        thickness = book["height"]

        # 좌 ↔ 우 번갈아 계단식
        x_offset = (idx % 3) * 1.2 * offset_direction
        offset_direction *= -1

        # 책 박스
        rect = plt.Rectangle(
            (3 + x_offset, y),
            6,               # 가로길이
            thickness,       # 세로길이
            color=color,
            ec="black",
            linewidth=2
        )
        ax.add_patch(rect)

        # 책 제목만 표시
        ax.text(
            3 + x_offset + 3,
            y + thickness / 2,
            f"{book['title']}",        # ⬅ 제목만!
            fontsize=13,
            color="black",
            fontproperties=font_prop,
            weight="bold",
            ha="center",
            va="center"
        )

        # ✔ 텀 제거 (완전 딱 붙게)
        y += thickness + 0.05    # 아주 미세한 간격만 두기 (겹침 방지)

    ax.axis("off")
    st.pyplot(fig)
