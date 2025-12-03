"""
CLI Tool for Shorts Generation
"""

import click
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shorts import RankingShortsGenerator


@click.group()
def cli():
    """YouTube Shorts Auto Generator"""
    pass


@cli.group()
def shorts():
    """Generate shorts videos"""
    pass


@shorts.command()
@click.option('--input', '-i', type=click.Path(exists=True),
              help='Input CSV file path (mutually exclusive with --input_dir)')
@click.option('--input-dir', type=click.Path(exists=True),
              help='Input directory with video files (mutually exclusive with --input)')
@click.option('--output', '-o', default='output/videos',
              help='Output directory (default: output/videos)')
@click.option('--style', '-s', default='modern',
              help='Template style (default: modern)')
@click.option('--aspect', '-a', default='9:16',
              type=click.Choice(['9:16', '16:9']),
              help='Aspect ratio (default: 9:16)')
@click.option('--bgm', '-b', type=click.Path(exists=True),
              help='BGM file path (optional)')
@click.option('--bgm-volume', default=0.3, type=float,
              help='BGM volume 0.0-1.0 (default: 0.3)')
@click.option('--bgm-drops', type=str,
              help='BGM drop times in seconds, comma-separated (e.g., "0,8,16,24")')
@click.option('--top', type=int,
              help='Use only top N videos (for --input-dir mode)')
@click.option('--order', type=click.Choice(['desc', 'asc']), default='desc',
              help='Ranking order: desc (N→1) or asc (1→N) (default: desc)')
@click.option('--title-mode', type=click.Choice(['manual', 'local', 'ai']), default='manual',
              help='Title generation mode (default: manual)')
@click.option('--titles', type=click.Path(exists=True),
              help='Titles CSV file (for manual mode)')
@click.option('--no-rail', is_flag=True,
              help='Disable left-side ranking rail')
@click.option('--no-intro', is_flag=True,
              help='Disable title intro overlay')
def ranking(input, input_dir, output, style, aspect, bgm, bgm_volume, bgm_drops,
            top, order, title_mode, titles, no_rail, no_intro):
    """Generate ranking-style shorts video"""

    click.echo(f"\n{'='*60}")
    click.echo(f"YouTube Shorts Generator - Ranking Type")
    click.echo(f"{'='*60}\n")

    # 입력 모드 검증
    if not input and not input_dir:
        click.echo("❌ Error: Must provide either --input or --input-dir")
        sys.exit(1)

    if input and input_dir:
        click.echo("❌ Error: Cannot use both --input and --input-dir")
        sys.exit(1)

    try:
        # Initialize generator
        generator = RankingShortsGenerator(style=style, aspect_ratio=aspect)

        # CSV 모드
        if input:
            # Validate CSV
            click.echo("📋 Validating CSV...")
            if not generator.validate_csv(input):
                click.echo("\n❌ CSV validation failed!")
                sys.exit(1)

            # Generate video
            click.echo("\n🎬 Starting video generation (CSV mode)...")
            result = generator.generate_from_csv(
                csv_path=input,
                output_dir=output,
                bgm_path=bgm,
                bgm_drops=bgm_drops,
                enable_rail=not no_rail,
                enable_intro=not no_intro
            )

        # 폴더 모드
        else:
            click.echo("\n🎬 Starting video generation (Folder mode)...")
            result = generator.generate_from_dir(
                input_dir=input_dir,
                output_dir=output,
                top=top,
                order=order,
                title_mode=title_mode,
                titles_csv=titles,
                bgm_path=bgm,
                bgm_drops=bgm_drops,
                enable_rail=not no_rail,
                enable_intro=not no_intro
            )

        click.echo(f"{'='*60}")
        click.echo(f"✅ Success!")
        click.echo(f"📹 Output: {result}")
        click.echo(f"{'='*60}\n")

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def version():
    """Show version"""
    from src import __version__
    click.echo(f"v{__version__}")


if __name__ == '__main__':
    cli()
