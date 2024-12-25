"""This is a boilerplate pipeline 'main' generated using Kedro 0.19.10."""
from kedro.pipeline import Pipeline, pipeline, node
from .nodes import *


def create_pipeline(**kwargs) -> Pipeline:
  """Execute the nodes of the pipeline in order."""
  return pipeline([
      node(
          name='extract_cambridge',
          func=extract_cambridge,
          inputs='params:extract_path',
          outputs='cambridge'
      ),
      node(
          name='transform',
          func=transform,
          inputs=[
              'cambridge'
          ],
          outputs='union'
      ),
      node(
          name='telegram',
          func=telegram,
          inputs=[
              'union'
          ],
          outputs=None
      ),

  ])  # type: ignore
