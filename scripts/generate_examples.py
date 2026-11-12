"""Generate deterministic examples.json for the web playground.

Executes the pipeline with FakeModelClient to produce 100% authentic GradeResult
objects for four synthetic scenarios in both English and Portuguese.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from ad_copy_grader.llm import FakeModelClient
from ad_copy_grader.models import AdInput
from ad_copy_grader.pipeline import grade

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "web" / "examples.json"


async def generate_scenario_1() -> dict[str, Any]:
    """Generate clean 10/10 compliant RSA ad scenario."""
    input_en = AdInput(
        headlines=[
            "Dental Implants Clinic",
            "Top Dental Implants",
            "Best Dental Implants Care",
            "Experienced Surgeons",
            "Modern Dentistry",
            "Sedation Options Available",
            "Digital Smile Design",
            "Restore Your Smile Today",
            "Flexible Payment Plans",
            "Cutting-Edge 3D Scans",
            "Natural-Looking Results",
            "Full Arch Replacements",
            "Trusted Dental Clinic",
            "Book Your Evaluation Today",
            "Convenient Downtown Clinic",
        ],
        descriptions=[
            "Restore your smile with permanent dental implants. Schedule your consultation today.",
            (
                "Experienced oral surgeons, 3D digital imaging, and comfortable sedation"
                " options available."
            ),
        ],
        primary_service="Dental Implants",
        final_url="https://example.com/dental-implants",
        path1="implants",
        path2="austin",
        lp_context=(
            "Specialist dental implant clinic. Single tooth and full arch implants."
            " Comprehensive initial consultation available."
        ),
        lang="en",
    )

    input_pt = AdInput(
        headlines=[
            "Implante Dentário em SP",
            "Clínica de Implante Dentário",
            "Implante Dentário Moderno",
            "Cirurgiões Credenciados",
            "Recupere Seu Sorriso",
            "Sedação Consciente Segura",
            "Planejamento Digital 3D",
            "Atendimento Humanizado",
            "Opções de Parcelamento",
            "Tecnologia Odontológica",
            "Resultados Naturais",
            "Prótese Sobre Implante",
            "Consultório Especializado",
            "Agende Sua Avaliação Hoje",
            "Unidade de Fácil Acesso",
        ],
        descriptions=[
            "Recupere seu sorriso com implante dentário seguro. Agende sua avaliação conosco hoje.",
            (
                "Cirurgiões experientes, tomografia 3D e opções de sedação consciente para seu"
                " conforto."
            ),
        ],
        primary_service="Implante Dentário",
        final_url="https://example.com/implante-dentario",
        path1="implantes",
        path2="sp",
        lp_context=(
            "Clínica de implante dentário especializada em reabilitação oral. Agende sua avaliação."
        ),
        lang="pt",
    )

    client = FakeModelClient()
    res_en = await grade(input_en, client)
    res_pt = await grade(input_pt, client)

    return {
        "id": "clean_10_of_10",
        "label": {
            "en": "Clean Compliant RSA (10/10)",
            "pt": "Anúncio Conforme e Limpo (10/10)",
        },
        "description": {
            "en": (
                "Fully compliant 15-headline RSA with verified primary service, compliant"
                " lengths, and strong CTAs."
            ),
            "pt": (
                "Anúncio RSA com 15 títulos em total conformidade, serviços verificados e CTAs"
                " claras."
            ),
        },
        "input": {
            "en": input_en.model_dump(mode="json"),
            "pt": input_pt.model_dump(mode="json"),
        },
        "result": {
            "en": res_en.final.model_dump(mode="json"),
            "pt": res_pt.final.model_dump(mode="json"),
        },
        "dropped_issues": {
            "en": [],
            "pt": [],
        },
    }


async def generate_scenario_2() -> dict[str, Any]:
    """Generate unverified price claim A01 scenario."""
    input_en = AdInput(
        headlines=[
            "Emergency Plumbing Austin",
            "Plumbing Starting At $499",
            "Top Emergency Plumbing",
            "Best Emergency Plumbing Care",
            "Licensed Plumbers Near You",
            "Fast 24/7 Leak Repair",
            "Local Austin Technicians",
            "Water Heater Replacement",
            "Drain Cleaning Experts",
            "No Hidden Dispatch Fees",
            "Rapid Response Team",
            "Affordable Pipe Services",
            "Call Austin Plumbers Today",
            "Trusted Residential Repairs",
            "Book Immediate Service",
        ],
        descriptions=[
            "Need urgent plumbing repairs in Austin? Call our licensed technicians right now.",
            "Comprehensive pipe leak fixes, drain cleaning, and emergency fixture replacements.",
        ],
        primary_service="Emergency Plumbing",
        final_url="https://example.com/emergency-plumbing",
        path1="plumbing",
        path2="austin",
        lp_context=(
            "Premier emergency plumbing dispatch in Austin. Standard dispatch rate is $899."
            " Licensed plumbers available 24/7."
        ),
        lang="en",
    )

    input_pt = AdInput(
        headlines=[
            "Encanador 24 Horas em SP",
            "Atendimento a Partir R$ 499",
            "Serviço de Encanador 24 Horas",
            "Melhor Encanador 24 Horas",
            "Técnicos em Encanamento",
            "Reparo Rápido de Vazamentos",
            "Caça Vazamentos Preciso",
            "Desentupimento Residencial",
            "Troca de Tubulações em SP",
            "Sem Taxas Escondidas",
            "Chegada Rápida no Local",
            "Preços Transparentes",
            "Ligue Para Nossos Técnicos",
            "Atendimento Para Empresas",
            "Chame Nossa Equipe Hoje",
        ],
        descriptions=[
            (
                "Precisa de encanador urgente em São Paulo? Ligue para nossos técnicos certificados"
                " agora."
            ),
            "Conserto de vazamentos, desentupimento e substituição rápida de canos com garantia.",
        ],
        primary_service="Encanador 24 Horas",
        final_url="https://example.com/encanador-24h",
        path1="encanador",
        path2="sp",
        lp_context=(
            "Serviços de encanamento de urgência em São Paulo. Taxa padrão de atendimento a partir"
            " de R$ 390. Profissionais qualificados."
        ),
        lang="pt",
    )

    client = FakeModelClient()
    res_en = await grade(input_en, client)
    res_pt = await grade(input_pt, client)

    return {
        "id": "unverified_price_a01",
        "label": {
            "en": "Unverified Price Claim (A01)",
            "pt": "Preço Não Confirmado na LP (A01)",
        },
        "description": {
            "en": (
                "Headline claims an unverified offer ($499) conflicting with landing page ($899),"
                " triggering A01 and a validated rewrite."
            ),
            "pt": (
                "Título anuncia preço não verificado (R$ 499) divergente da landing page"
                " (R$ 390), acionando A01 e reescrita validada."
            ),
        },
        "input": {
            "en": input_en.model_dump(mode="json"),
            "pt": input_pt.model_dump(mode="json"),
        },
        "result": {
            "en": res_en.final.model_dump(mode="json"),
            "pt": res_pt.final.model_dump(mode="json"),
        },
        "dropped_issues": {
            "en": [],
            "pt": [],
        },
    }


async def generate_scenario_3() -> dict[str, Any]:
    """Generate verified price authority filter scenario with stripped LLM false positive."""
    input_en = AdInput(
        headlines=[
            "Dental Implants Clinic",
            "Dental Implants From $899",
            "Top Dental Implants",
            "Best Dental Implants Care",
            "Experienced Surgeons",
            "Modern Dentistry",
            "Sedation Options Available",
            "Digital Smile Design",
            "Restore Your Smile Today",
            "Flexible Payment Plans",
            "Cutting-Edge 3D Scans",
            "Natural-Looking Results",
            "Full Arch Replacements",
            "Trusted Dental Clinic",
            "Book Your Evaluation Today",
        ],
        descriptions=[
            "Restore your smile with permanent dental implants. Schedule your consultation today.",
            (
                "Experienced oral surgeons, 3D digital imaging, and comfortable sedation"
                " options available."
            ),
        ],
        primary_service="Dental Implants",
        final_url="https://example.com/dental-implants",
        path1="implants",
        path2="austin",
        lp_context=(
            "Specialist dental implant clinic. Single tooth implants starting from $899 including"
            " initial scan. Consultation available."
        ),
        lang="en",
    )

    input_pt = AdInput(
        headlines=[
            "Implante Dentário em SP",
            "Implantes a Partir de R$ 390",
            "Clínica de Implante Dentário",
            "Implante Dentário Moderno",
            "Cirurgiões Credenciados",
            "Recupere Seu Sorriso",
            "Sedação Consciente Segura",
            "Planejamento Digital 3D",
            "Atendimento Humanizado",
            "Opções de Parcelamento",
            "Tecnologia Odontológica",
            "Resultados Naturais",
            "Prótese Sobre Implante",
            "Consultório Especializado",
            "Agende Sua Avaliação Hoje",
        ],
        descriptions=[
            "Recupere seu sorriso com implante dentário seguro. Agende sua avaliação conosco hoje.",
            (
                "Cirurgiões experientes, tomografia 3D e opções de sedação consciente para seu"
                " conforto."
            ),
        ],
        primary_service="Implante Dentário",
        final_url="https://example.com/implante-dentario",
        path1="implantes",
        path2="sp",
        lp_context=(
            "Clínica especializada em reabilitação oral. Implante unitário com coroa a partir de"
            " R$ 390 mensais na avaliação."
        ),
        lang="pt",
    )

    fake_llm_json_en = json.dumps(
        {
            "issues": [
                {
                    "rule_id": "A01",
                    "severity": "error",
                    "message": "Price or offer '$899' in headline not verified in landing page.",
                    "location": {"field": "headline", "index": 1},
                }
            ],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [
                {
                    "location": {"field": "headline", "index": 1},
                    "original": "Dental Implants From $899",
                    "suggested": "Dental Implants Today",
                    "reason": "Removes unverified price claim.",
                }
            ],
        }
    )

    fake_llm_json_pt = json.dumps(
        {
            "issues": [
                {
                    "rule_id": "A01",
                    "severity": "error",
                    "message": "Preço ou oferta 'R$ 390' no título não confirmado na landing page.",
                    "location": {"field": "headline", "index": 1},
                }
            ],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [
                {
                    "location": {"field": "headline", "index": 1},
                    "original": "Implantes a Partir de R$ 390",
                    "suggested": "Implantes Dentários Hoje",
                    "reason": "Remove preço não verificado na página.",
                }
            ],
        }
    )

    client_en = FakeModelClient(responses=[fake_llm_json_en])
    client_pt = FakeModelClient(responses=[fake_llm_json_pt])

    res_en = await grade(input_en, client_en)
    res_pt = await grade(input_pt, client_pt)

    dropped_en = [
        iss.model_dump(mode="json")
        for iss in res_en.raw.issues
        if iss.rule_id not in [f.rule_id for f in res_en.final.issues]
    ]
    dropped_pt = [
        iss.model_dump(mode="json")
        for iss in res_pt.raw.issues
        if iss.rule_id not in [f.rule_id for f in res_pt.final.issues]
    ]

    return {
        "id": "verified_price_authority_filter",
        "label": {
            "en": "Verified Price (Code Authority Filter)",
            "pt": "Preço Verificado (Filtro de Autoridade)",
        },
        "description": {
            "en": (
                "Headline price ($899 / R$ 390) exists in LP context. Raw LLM emitted an A01 false"
                " positive, which the server Code Authority Filter stripped."
            ),
            "pt": (
                "O preço no anúncio está na landing page. O LLM gerou um falso positivo (A01), que"
                " o Filtro de Autoridade determinístico descartou."
            ),
        },
        "input": {
            "en": input_en.model_dump(mode="json"),
            "pt": input_pt.model_dump(mode="json"),
        },
        "result": {
            "en": res_en.final.model_dump(mode="json"),
            "pt": res_pt.final.model_dump(mode="json"),
        },
        "dropped_issues": {
            "en": dropped_en,
            "pt": dropped_pt,
        },
    }


async def generate_scenario_4() -> dict[str, Any]:
    """Generate clinical guarantee and deterministic code errors scenario."""
    input_en = AdInput(
        headlines=[
            "Laser Eye Surgery Clinic",
            "100% Guaranteed Results",
            "Comprehensive Laser Vision Correction Center",
            "Laser Eye Surgery Clinic",
            "Top Laser Eye Surgery Care",
            "Best Laser Eye Surgery Doctors",
            "Modern Blade-Free LASIK",
            "Rapid Visual Recovery",
            "Experienced Eye Surgeons",
            "Free LASIK Consultation",
            "Advanced Vision Technology",
            "Affordable Financing Plans",
            "Downtown Laser Vision Care",
            "Schedule An Exam Today",
            "Clear Vision Without Glasses",
        ],
        descriptions=[
            "Transform your vision with blade-free LASIK. Schedule your consultation today.",
            "Experienced eye surgeons, advanced laser technology, and rapid visual recovery.",
        ],
        primary_service="Laser Eye Surgery",
        final_url="https://example.com/laser-eye-surgery",
        path1="vision",
        path2="lasik",
        lp_context=(
            "Advanced laser eye surgery and vision correction center. Comprehensive exams"
            " available."
        ),
        lang="en",
    )

    input_pt = AdInput(
        headlines=[
            "Implantes Dentários em SP",
            "Implante 100% Garantido",
            "Reabilitação Oral Avançada e Implantes Dentários",
            "Implantes Dentários em SP",
            "Melhores Implantes em SP",
            "Clínica de Implantes",
            "Cirurgia Segura e Conforto",
            "Recuperação Rápida",
            "Cirurgiões Credenciados",
            "Avaliação Completa Hoje",
            "Tecnologia Digital 3D",
            "Opções de Parcelamento",
            "Consultório Especializado",
            "Agende Sua Avaliação Hoje",
            "Recupere Seu Sorriso",
        ],
        descriptions=[
            (
                "Recupere seu sorriso com implantes de alta precisão. Agende sua avaliação conosco"
                " hoje."
            ),
            (
                "Cirurgiões experientes, tomografia 3D e opções de sedação consciente para seu"
                " conforto."
            ),
        ],
        primary_service="Implantes",
        final_url="https://example.com/implantes",
        path1="implantes",
        path2="sp",
        lp_context=(
            "Clínica de reabilitação oral e implantes dentários. Avaliação inicial disponível."
        ),
        lang="pt",
    )

    client = FakeModelClient()
    res_en = await grade(input_en, client)
    res_pt = await grade(input_pt, client)

    return {
        "id": "clinical_guarantee_plus_code_errors",
        "label": {
            "en": "Clinical Guarantee & Code Errors (Hybrid)",
            "pt": "Garantia Clínica e Erros de Código (Híbrido)",
        },
        "description": {
            "en": (
                "Demonstrates hybrid grading: deterministic code errors (D04 length >30, D08"
                " duplicate) alongside LLM semantic warning (A03 medical guarantee) with"
                " validated rewrite."
            ),
            "pt": (
                "Demonstra auditoria híbrida: regras determinísticas (D04 >30 caracteres, D08"
                " duplicado) e aviso semântico LLM (A03 promessa médica) com sugestão validada."
            ),
        },
        "input": {
            "en": input_en.model_dump(mode="json"),
            "pt": input_pt.model_dump(mode="json"),
        },
        "result": {
            "en": res_en.final.model_dump(mode="json"),
            "pt": res_pt.final.model_dump(mode="json"),
        },
        "dropped_issues": {
            "en": [],
            "pt": [],
        },
    }


async def main() -> None:
    """Run all generators and write web/examples.json."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    scenarios = [
        await generate_scenario_1(),
        await generate_scenario_2(),
        await generate_scenario_3(),
        await generate_scenario_4(),
    ]
    content = json.dumps(scenarios, indent=2, ensure_ascii=False) + "\n"
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Generated {len(scenarios)} scenarios into {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
