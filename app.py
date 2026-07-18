async def process_consultation(query: str, is_reading: bool = False, reading_data: dict | None = None) -> None:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        prefix = ""
        lang = st.session_state.lang

        if is_reading and reading_data:
            primary_bits = reading_data["primary_bits"]
            trans_bits = reading_data["transformed_bits"]
            primary_hex = HEXAGRAM_PROFILES[primary_bits]
            feng_shui_summary = describe_hexagram_feng_shui(primary_hex)
            columns = st.columns(2)
            with columns[0]:
                st.markdown(render_hexagram_svg(primary_bits, translate("primary_hex", lang)), unsafe_allow_html=True)
                st.write(f"#{primary_hex['number']} {primary_hex['name_en']}")
                st.caption(f"{translate('theme_label', lang)}: {primary_hex['theme']}")

                st.caption(feng_shui_summary["summary"])
            if trans_bits:
                trans_hex = HEXAGRAM_PROFILES[trans_bits]
                with columns[1]:
                    st.markdown(render_hexagram_svg(trans_bits, translate("trans_hex", lang)), unsafe_allow_html=True)
                    st.write(f"#{trans_hex['number']} {trans_hex['name_en']}")

            prefix = "The coins have been cast.\n\n"
            language_names = {"en": "English", "id": "Bahasa Indonesia", "zh": "Traditional Chinese"}
            prompt = f"""
Please respond in {language_names.get(lang, 'English')}.
Provide a structured I Ching reading for: {query}

Intention context (it did not determine this cast): {reading_data['intention_summary']}
Primary Hexagram: #{primary_hex['number']} - {primary_hex['name_en']}

Structure your response with these headers:
### {translate('the_judgment', lang)}
### {translate('the_image', lang)}
### {translate('changing_lines', lang)}
### {translate('master_strategy', lang)}
"""
            if trans_bits:
                prompt += f"\nChanging lines: {reading_data['changing_lines']}"
                prompt += f"\nTransformed Hexagram: #{HEXAGRAM_PROFILES[trans_bits]['number']}"

            prompt += f"\n\nFeng Shui Summary:\n{feng_shui_summary['summary']}"
        else:
            prompt = query

        def on_token(token: str) -> None:
            nonlocal full_response
            full_response += token
            response_placeholder.markdown(
                f"<div class='oracle-response'><h3>{translate('oracle_guidance', lang)}</h3>\n\n{prefix}{full_response}</div>",
                unsafe_allow_html=True,
            )

        final_text = await st.session_state.ascension.respond(prompt, on_token=on_token)
        response_placeholder.markdown(
            f"<div class='oracle-response'><h3>{translate('oracle_guidance', lang)}</h3>\n\n{prefix}{final_text}</div>",
            unsafe_allow_html=True,
        )
        st.session_state.messages.append({"role": "assistant", "content": final_text})

        if is_reading and reading_data:
            reading_id = str(uuid.uuid4())
            st.session_state.last_reading_id = reading_id
            st.session_state.last_hex_num = primary_hex["number"]
            save_reading({
                "reading_id": reading_id,
                "user_id": st.session_state.user_id,
                "timestamp": time.time(),
                "hexagram_number": primary_hex["number"],
                "hexagram_name": primary_hex["name_en"],
                "oracle_response": final_text,
                "intention_summary": reading_data["intention_summary"],
                "changing_lines": reading_data["changing_lines"],
            })
