"""
Master pipeline runner - Execute entire data pipeline
"""

import subprocess
import sys
from config.logger import logger

def run_pipeline():
    """Execute complete pipeline sequentially"""
    
    logger.info("\n" + "="*70)
    logger.info("SALES PERFORMANCE DASHBOARD - COMPLETE PIPELINE")
    logger.info("="*70)
    
    steps = [
        ("Generate Sample Data", "python src/data/generate_sample_data.py"),
        ("Load to MySQL", "python src/data/load_to_mysql.py"),
        ("Execute SQL Cleaning", "python src/data/execute_sql_cleaning.py"),
        ("Run ETL Pipeline", "python src/etl/etl_pipeline.py"),
        ("Generate EDA Analysis", "python src/analysis/eda_analysis.py"),
        ("Create Excel Reports", "python src/output/excel_generator.py"),
        ("Export Power BI Data", "python src/output/generate_powerbi_data.py"),
    ]
    
    completed = 0
    failed = []
    
    for step_name, command in steps:
        logger.info(f"\n{'─'*70}")
        logger.info(f"📍 STEP {completed + 1}: {step_name}")
        logger.info(f"{'─'*70}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=False)
            if result.returncode == 0:
                completed += 1
                logger.info(f"✅ {step_name} - SUCCESS")
            else:
                failed.append(step_name)
                logger.error(f"❌ {step_name} - FAILED")
        except Exception as e:
            failed.append(step_name)
            logger.error(f"❌ {step_name} - ERROR: {e}")
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("PIPELINE SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"✅ Completed: {completed}/{len(steps)}")
    if failed:
        logger.info(f"❌ Failed: {', '.join(failed)}")
    else:
        logger.info("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    
    logger.info(f"\n📊 Output Files Generated:")
    logger.info(f"  ✓ data/processed/sales_data_cleaned.csv")
    logger.info(f"  ✓ output/dashboards/eda_figures/ (4 PNG files)")
    logger.info(f"  ✓ output/excel/sales_report.xlsx")
    logger.info(f"  ✓ output/powerbi_data/ (CSV tables)")
    logger.info(f"  ✓ logs/sales_dashboard_*.log")
    
    logger.info(f"\n📖 Next Steps:")
    logger.info(f"  1. Open output/excel/sales_report.xlsx for monthly reporting")
    logger.info(f"  2. Create Power BI dashboard from output/powerbi_data/")
    logger.info(f"  3. Push to GitHub: git add . && git commit -m 'Project execution'")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Pipeline error: {e}")
        sys.exit(1)