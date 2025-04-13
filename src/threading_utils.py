import threading
from typing import List, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod

class ThreadingManager(ABC):
    """Abstract base class for threading managers"""
    
    @abstractmethod
    def process_in_parallel(self, 
                          items: List[Any], 
                          process_func: Callable[[Any, int], Any],
                          chunk_handler: Optional[Callable[[int, List[Any], Dict[int, Any]], List[Any]]] = None,
                          max_threads: int = 6) -> List[Any]:
        """Process items in parallel"""
        pass

class BatchProcessor(ThreadingManager):
    """Processes items in batches using multiple threads"""
    
    def process_in_parallel(self, 
                          items: List[Any], 
                          process_func: Callable[[Any, int], Any],
                          chunk_handler: Optional[Callable[[int, List[Any], Dict[int, Any]], List[Any]]] = None,
                          max_threads: int = 6) -> List[Any]:
        """
        Process a list of items in parallel using multiple threads.
        
        Args:
            items: List of items to process
            process_func: Function to process each item, takes (item, index) and returns result
            chunk_handler: Optional function to handle batch results, takes (chunk_start_index, chunk, results_dict)
            max_threads: Maximum number of threads to use
            
        Returns:
            List of processed results
        """
        # Divide items into chunks
        chunks = self._divide_chunks(items, max_threads)
        results = {}
        result_list = []
        
        # Process each chunk in parallel
        for i, chunk in enumerate(chunks):
            threads = []
            
            # Create and start threads for this chunk
            for ii, item in enumerate(chunk):
                index = i * max_threads + ii
                thread = threading.Thread(
                    target=self._thread_worker, 
                    args=(item, index, process_func, results)
                )
                threads.append(thread)
                thread.start()
                
            # Wait for all threads in this chunk to complete
            for thread in threads:
                thread.join()
                
            # Process results for this chunk if handler provided
            if chunk_handler:
                chunk_results = chunk_handler(i * max_threads, chunk, results)
                result_list.extend(chunk_results)
            else:
                # Default behavior: collect results in order
                for ii in range(len(chunk)):
                    index = i * max_threads + ii
                    if index in results:
                        result_list.append(results[index])
        
        return result_list
    
    def _thread_worker(self, item: Any, index: int, process_func: Callable, results: Dict[int, Any]) -> None:
        """Worker function for each thread"""
        results[index] = process_func(item, index)
    
    def _divide_chunks(self, items: List[Any], chunk_size: int) -> List[List[Any]]:
        """Divide a list into chunks of specified size"""
        chunks = []
        for i in range(0, len(items), chunk_size):
            chunks.append(items[i:i + chunk_size])
        return chunks