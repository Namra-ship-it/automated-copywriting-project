"""Command-line interface for the copywriting engine."""

import argparse
import asyncio
import sys


from loguru import logger

from src.batch_handler import BatchHandler
from src.config import Config
from src.generator import CopyGenerator
from src.main import setup_logging
from src.models import CopyRequest, Platform, Tone
from src.utils import write_json_file


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Automated Copywriting & Tone Transformer - DeepSeek API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python src/cli.py --interactive

  # Real-time single request
     python src/cli.py --product "EcoCharge Pro" --description "..."
    --platform Instagram --tone Eco-conscious --audience "..." --cta "Shop now"
  # Batch from file
  python src/cli.py --batch --input-file examples/sample_inputs.json --output-file outputs/batch/results.json
        """,
    )

    # Required arguments for real-time mode
    parser.add_argument("--product", type=str, help="Product name")
    parser.add_argument("--description", type=str, help="Product description")
    parser.add_argument(
        "--platform",
        type=str,
        choices=[p.value for p in Platform],
        help="Target platform",
    )
    parser.add_argument(
        "--tone",
        type=str,
        choices=[t.value for t in Tone],
        help="Desired tone",
    )
    parser.add_argument("--audience", type=str, help="Target audience description")
    parser.add_argument("--cta", type=str, help="Call-to-action phrase")

    # Optional arguments
    parser.add_argument(
        "--char-limit",
        type=int,
        default=3000,
        help="Character limit (default: 3000)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=Config.DEFAULT_TEMPERATURE,
        help=f"Temperature 0.0-2.0 (default: {Config.DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=Config.DEFAULT_TOP_P,
        help=f"Top_P 0.0-1.0 (default: {Config.DEFAULT_TOP_P})",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=Config.DEFAULT_MAX_TOKENS,
        help=f"Max tokens (default: {Config.DEFAULT_MAX_TOKENS})",
    )

    # Mode switches
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with prompts",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run in batch mode (requires --input-file)",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Input JSON file for batch mode",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Output file path for results",
    )

    # Utility
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit",
    )

    return parser


def validate_args(args: argparse.Namespace) -> list[str]:
    """Validate CLI arguments.

    Args:
        args: Parsed arguments.

    Returns:
        List of validation error messages.
    """
    errors: list[str] = []

    if args.validate_config:
        return errors

    if args.interactive:
        return errors

    if args.batch:
        if not args.input_file:
            errors.append("--batch requires --input-file")
        return errors

    # Real-time mode requires all core fields
    required = [
        ("--product", args.product),
        ("--description", args.description),
        ("--platform", args.platform),
        ("--tone", args.tone),
        ("--audience", args.audience),
        ("--cta", args.cta),
    ]
    for name, value in required:
        if not value:
            errors.append(f"Real-time mode requires {name}")

    if not (0.0 <= args.temperature <= 2.0):
        errors.append("--temperature must be between 0.0 and 2.0")

    if not (0.0 <= args.top_p <= 1.0):
        errors.append("--top-p must be between 0.0 and 1.0")

    return errors


def interactive_mode() -> None:
    """Run interactive mode with user prompts."""
    print("\n🚀 Automated Copywriting & Tone Transformer\n")
    print("Enter your request details:\n")

    product = input("Product Name: ").strip()
    description = input("Product Description: ").strip()
    platform = input(f"Platform ({', '.join(p.value for p in Platform)}): ").strip()
    tone = input(f"Tone ({', '.join(t.value for t in Tone)}): ").strip()
    audience = input("Target Audience: ").strip()
    cta = input("Call to Action: ").strip()
    char_limit = int(input("Character Limit [2200]: ").strip() or "2200")
    temperature = float(input("Temperature [0.7]: ").strip() or "0.7")
    top_p = float(input("Top_P [0.9]: ").strip() or "0.9")

    request = CopyRequest(
        product_name=product,
        product_description=description,
        platform=Platform(platform),
        tone=Tone(tone),
        target_audience=audience,
        character_limit=char_limit,
        call_to_action=cta,
        temperature=temperature,
        top_p=top_p,
    )

    print("\n⏳ Generating copy...\n")
    generator = CopyGenerator()
    response = asyncio.run(generator.generate_async(request))

    print("\n✅ Result:\n")
    print(response.to_json())


def real_time_mode(args: argparse.Namespace) -> None:
    """Run real-time single request mode.

    Args:
        args: Parsed CLI arguments.
    """
    request = CopyRequest(
        product_name=args.product,
        product_description=args.description,
        platform=Platform(args.platform),
        tone=Tone(args.tone),
        target_audience=args.audience,
        character_limit=args.char_limit,
        call_to_action=args.cta,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )

    generator = CopyGenerator()
    response = asyncio.run(generator.generate_async(request))

    if args.output_file:
        write_json_file(args.output_file, response.to_dict())
        print(f"Result saved to {args.output_file}")
    else:
        print(response.to_json())


def batch_mode(args: argparse.Namespace) -> None:
    """Run batch processing mode.

    Args:
        args: Parsed CLI arguments.
    """
    handler = BatchHandler()
    output_path = handler.process_file(args.input_file, args.output_file)
    print(f"Batch results saved to {output_path}")


def main() -> None:
    """Main CLI entry point."""
    setup_logging()

    parser = create_parser()
    args = parser.parse_args()

    if args.validate_config:
        errors = Config.validate()
        if errors:
            print("❌ Configuration errors:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("✅ Configuration is valid.")
            sys.exit(0)

    validation_errors = validate_args(args)
    if validation_errors:
        print("❌ Validation errors:")
        for err in validation_errors:
            print(f"  - {err}")
        parser.print_help()
        sys.exit(1)

    try:
        if args.interactive:
            interactive_mode()
        elif args.batch:
            batch_mode(args)
        else:
            real_time_mode(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception("CLI execution failed")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
